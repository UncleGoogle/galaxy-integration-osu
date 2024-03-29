import sys
import time
import psutil
import json
import os
import subprocess
import shutil
from pathlib import Path
from glob import glob

from invoke import task
from galaxy.tools import zip_folder_to_file
import github


with open('src/manifest.json') as f:
    __version__ = json.load(f)['version']


REQUIREMENTS = 'requirements/app.in'
REQUIREMENTS_DEV = 'requirements/dev.in'
REQUIREMENTS_LOCK = 'requirements/lock/app.txt'
REQUIREMENTS_DEV_LOCK = 'requirements/lock/dev.txt'

GALAXY_PATH = ''
DIST_DIR = ''
GALAXY_PYTHONPATH = ''

if sys.platform == 'win32':
    PLATFORM = 'Windows'
    GALAXY_PATH = 'C:\\Program Files (x86)\\GOG Galaxy\\GalaxyClient.exe'
    DIST_DIR = os.environ['localappdata'] + '\\GOG.com\\Galaxy\\plugins\\installed'
    PYTHON = 'python'
    GALAXY_PYTHONPATH = str(Path(os.path.expandvars("%programfiles(x86)%")) / "GOG Galaxy" / "python" / "python.exe")
elif sys.platform == 'darwin':
    PLATFORM = 'Mac'
    GALAXY_PATH = "/Applications/GOG Galaxy.app/Contents/MacOS/GOG Galaxy"
    DIST_DIR = os.environ['HOME'] + r"/Library/Application\ Support/GOG.com/Galaxy/plugins/installed"
    PYTHON = 'python3'

DIST_PLUGIN = os.path.join(DIST_DIR, 'osu')
THIRD_PARTY_RELATIVE_DEST = 'modules'



def get_repo():
    token = os.environ['GITHUB_TOKEN']
    g = github.Github(token)
    return g.get_repo('UncleGoogle/galaxy-integration-osu')


def asset_name(tag, platform):
    return f'osu_{tag}_{platform[:3].lower()}.zip'


@task
def install(c, dev=False):
    req = REQUIREMENTS_DEV_LOCK if dev else REQUIREMENTS_LOCK
    c.run(f"{PYTHON} -m pip install -r {req}")


@task
def lock(c, dev=False):
    req_in = REQUIREMENTS_DEV if dev else REQUIREMENTS
    req_out = REQUIREMENTS_DEV_LOCK if dev else REQUIREMENTS_LOCK
    c.run(f"pip-compile --generate-hashes --output-file={req_out} {req_in}")


@task
def build(c, output=DIST_PLUGIN):
    print(f'Preparing build to folder `{output}`')

    output = Path(output).resolve()
    print('Removing', output)
    if os.path.exists(output):
        try:
            shutil.rmtree(output)
        except OSError as e:
            if hasattr(e, 'winerror') and e.winerror in [145, 5]:
                # something e.g. antivirus check holds a file. Try to wait to be released for a moment
                time.sleep(3)
                shutil.rmtree(output)
            else:
                raise

    print('Copying source code to ', str(output))
    shutil.copytree('src', output, ignore=shutil.ignore_patterns(
        '__pycache__', '.mypy_cache', 'tests'))

    args = [
        PYTHON, "-m", "pip", "install",
        "-r", REQUIREMENTS_LOCK,
        "--target", str(output / THIRD_PARTY_RELATIVE_DEST),
        # "--implementation", "cp",
        # "--python-version", "37",
        # "--no-deps"
    ]
    print(f'Running `{" ".join(args)}`')
    subprocess.check_call(args)


@task
def dist(c, output=DIST_PLUGIN, deps=False):
    this_plugin = 'plugin-egg'
    for proc in psutil.process_iter(attrs=['exe'], ad_value=''):
        if proc.info['exe'] == GALAXY_PYTHONPATH:
            if this_plugin in proc.cmdline()[-1]:
                print(f'Running plugin instance found!. Terminating...')
                proc.terminate()
                break
    if not deps:
        print('Build without dependencies')
        os.makedirs(output, exist_ok=True)
        copy(c, output)
    else:
        build(c, output)
    print("Now, click 'retry' for crashed plugin in Settings")


@task
def copy(c, output=DIST_PLUGIN):
    print(f'Copying source code to {output}')
    for file_ in glob("src/*.py"):
        shutil.copy(file_, output)
    shutil.copy('CHANGELOG.md', output)


@task
def test(c):
    c.run('pytest')


@task
def archive(c, zip_name=None, target=None):
    if target is None:
        build(c, 'build')
        target = 'build'
    if zip_name is None:
        zip_name = f'osu_{__version__}.zip'
    print(f'Zipping build from `{target}` to `{zip_name}`')

    zip_folder_to_file(target, zip_name)
    zip_path = Path('.') / zip_name
    return str(zip_path.resolve())


@task(aliases=['tag'])
def create_tag(c, tag=None):
    if tag is None:
        tag = 'v' + __version__
    branch = c.run("git rev-parse --abbrev-ref HEAD").stdout.strip()

    print(f'New tag version will be: [{tag}] on [{branch}] branch. Is it OK? (make sure new version is committed)')
    if input('y/n').lower() != 'y':
        return

    print(f'Creating and pushing a new tag `{tag}`.')
    c.run(f'git tag {tag}')
    c.run(f'git push origin {tag}')


@task
def release(c, automa=False):
    tag = 'v' + __version__
    if automa:
        print(f'Creating/updating release with assets for {PLATFORM} to version {tag}')
    else:
        print(f'New tag version for release will be: {tag}. is it OK?')
        if input('y/n').lower() != 'y':
            return

    repo = get_repo()

    for release in repo.get_releases():
        if release.tag_name == tag and release.draft:
            draft_release = release
            break
    else:
        print('No draft release with given tag found.')
        if not automa:
            create_tag(c, tag)

        print(f'Creating new release for tag `{tag}`')
        draft_release = repo.create_git_release(
            tag=tag,
            name=__version__,
            message="draft",
            draft=True,
            prerelease=not automa
        )

    build(c, output='build')
    test(c)
    asset_path = archive(c, target='build', zip_name=asset_name(tag, PLATFORM))

    print(f'Uploading asset for {PLATFORM}: {asset_path}')
    draft_release.upload_asset(asset_path)
