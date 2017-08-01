import git
import logging
import multiprocessing
import shutil
import subprocess
import tempfile
import os

class ktree(object):
    def __init__(self, uri, branch=None, wdir=None):
        self.wdir = os.path.expanduser(wdir) if wdir != None else tempfile.mkdtemp()
        self.uri = uri
        self.branch = branch if branch != None else "master"

        try:
            self.repo = git.Repo(self.wdir)
        except (git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError):
            self.repo = git.Repo.init(self.wdir)

        cfg = self.repo.config_reader()
        if (not cfg.has_section('remote "origin"')):
            self.repo.create_remote('origin', self.uri)
        elif (self.uri != cfg.get_value('remote "origin"', 'url')):
            self.cleanup()
            self.repo = git.Repo.init(self.wdir)
            self.repo.create_remote('origin', self.uri)

        logging.info("base repo url: %s", self.uri)
        logging.info("base branch: %s", self.branch)
        logging.info("work dir: %s", self.wdir)

    def getpath(self):
        return self.wdir

    def checkout(self):
        logging.info("fetching base repo")
        self.repo.remote().fetch()

        if not 'master' in self.repo.heads:
            self.repo.create_head('master',
                    self.repo.remote().refs[self.branch])

        logging.info("checking out %s branch", self.branch)
        self.repo.heads.master.checkout()
        self.repo.head.reset("origin/%s" % self.branch,
                             index = True,
                             working_tree = True)

    def cleanup(self):
        logging.info("cleaning up %s", self.wdir)
        shutil.rmtree(self.wdir)

    def getrname(self, uri):
        rname = uri.split('/')[-1].replace('.git', '') if not uri.endswith('/') else uri.split('/')[-2].replace('.git', '')
        cfg = self.repo.config_reader()
        while cfg.has_section('remote "%s"' % rname) and (uri !=
                cfg.get_value('remote "%s"' % rname, 'url')):
            print "Already exists '%s', adding _" % rname
            rname += '_'

        return rname

    def merge_git_branch(self, uri, branch="master"):
        rname = self.getrname(uri)
        try:
            remote = self.repo.remote(rname)
        except ValueError:
            remote = self.repo.create_remote(rname, uri)

        logging.info("merging %s: %s", rname, branch)
        try:
            remote.pull(branch)
        except git.exc.GitCommandError:
            logging.warning("failed to merge '%s' from %s, skipping", branch, rname)
            self.repo.head.reset(index = True, working_tree = True)

    def merge_patchwork_patch(self, uri):
        pass

class kbuilder(object):
    def __init__(self, path, basecfg, cfgtype = None):
        self.path = os.path.expanduser(path)
        self.basecfg = os.path.expanduser(basecfg)
        self.cfgtype = cfgtype if cfgtype != None else "olddefconfig"
        self._ready = 0

        logging.info("basecfg: %s", self.basecfg)
        logging.info("cfgtype: %s", self.cfgtype)

    def prepare(self, clean=True):
        if (clean):
            logging.info("cleaning up tree with mrproper")
            subprocess.check_call(["make", "-C", self.path, "mrproper"])
        shutil.copyfile(self.basecfg, "%s/.config" % self.path)
        logging.info("prepare config: make %s", self.cfgtype)
        subprocess.check_call(["make", "-C", self.path, self.cfgtype])
        self._ready = 1

    def getrelease(self):
        if not self._ready:
            self.prepare(False)

        mk = subprocess.Popen(["make",
                               "-C",
                               self.path,
                               "kernelrelease"],
                              stdout = subprocess.PIPE)
        (stdout, stderr) = mk.communicate()
        return stdout.split("\n")[-3]


    def mktgz(self, clean=True):
        self.prepare(clean)
        logging.info("building kernel")
        mk = subprocess.Popen(["make",
                               "-j%d" % multiprocessing.cpu_count(),
                               "-C",
                               self.path,
                               "targz-pkg"],
                              stdout = subprocess.PIPE)
        (stdout, stderr) = mk.communicate()
        # FIXME: not especially robust
        return "/".join([self.path, stdout.split("\n")[-3].split(" ")[-1]])
