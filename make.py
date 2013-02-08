#!/usr/bin/python

import argparse
import json
import os
import shutil
import subprocess
import sys
import webbrowser

# Script constants

languages_file = "config/languages.json"

with open(languages_file, "r") as fileHandle:
  languages = json.load(fileHandle)

upload_server_file = "config/upload_server.json"
buildRootDir = "build/"
archiveFile = "build.tgz"


# Main


def main():

  args = parser.parse_args()

  if args.wca:
    args.clean = True
    args.all = True
    args.pdf = True
    args.archive = True

  startingBranch = currentBranch()

  try:

    if args.clean:
      clean(args)

    if not args.do_not_build:
      build(args)

    if args.archive:
      archive(args)

    if args.upload:
      upload(args)

    if args.server:
      server(args)

  finally:

    if args.reset_to_master:
      checkoutWCADocs("master")
    else:
      checkoutWCADocs(startingBranch)


# Script Parameters


parser = argparse.ArgumentParser(
  description='Build the WCA Regulations site.',
  formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
  '--clean', '-c',
  action='store_true',
  default=False,
  help="Remove build directory first."
)

parser.add_argument(
  '--language', '-l',
  default=None,
  help="Check out the branch (of wca-documents) and " +
    "build into the appropriate subdirectory for the given language.",
  choices=languages
)

parser.add_argument(
  '--do-not-build', '-d',
  action='store_true',
  default=False,
  help="Don't build. Useful for server and archive options."
)

parser.add_argument(
  '--all', '-a',
  action='store_true',
  default=False,
  help="Build all languages."
)

parser.add_argument(
  '--fragment', '-f',
  action='store_true',
  default=False,
  help="Generate html fragment files, rather than standalone. " +
    "Note that translations may look like gibberish in a browser, " +
    "because they don't have a tag to specify UTF8 encoding."
)

parser.add_argument(
  '--pdf', '-p',
  action='store_true',
  default=False,
  help="Generate PDF."
)

parser.add_argument(
  '--archive', '-z',
  action='store_true',
  default=False,
  help="Produce a compressed archive of the build folder."
)

parser.add_argument(
  '--reset-to-master', '-m',
  action='store_true',
  default=False,
  help="Reset wca-documents by checking out master at the end. " +
    "Useful with -d in order to reset wca-documents-extra for commits."
)

parser.add_argument(
  '--upload', '-u',
  action='store_true',
  default=False,
  help="Upload to an SFTP server on completion, using rsync."
)

parser.add_argument(
  '--server', '-s',
  action='store_true',
  default=False,
  help="Run a local test server and open build directory."
)

parser.add_argument(
  '--wca', '-w',
  action='store_true',
  default=False,
  help="Full WCA release build. Equivalent to -capz. " +
    "Does *not* currently include -f."
)


# Clean

def clean(args):
  if os.path.exists(buildRootDir):
    shutil.rmtree(buildRootDir)
  subprocess.check_call(["rm", "-rf", archiveFile])


# Git Operations

def currentBranch():
  output = subprocess.check_output([
    "git",
    "--git-dir=./wca-documents/.git",
    "--work-tree=./wca-documents",
    "rev-parse",
    "--abbrev-ref",
    "HEAD"
  ])

  return output.strip()


def checkoutWCADocs(branchName):
  subprocess.check_call([
    "git",
    "--git-dir=./wca-documents/.git",
    "--work-tree=./wca-documents",
    "checkout",
    branchName
  ])


# Build!


def build(args):
  if args.all:
    [buildTranslation(args, lang) for lang in languages]
    checkoutWCADocs("official")

  elif args.language == None:
    buildToDirectory(args, "")

  elif args.language in languages:
    buildTranslation(args, args.language)

  print "Finished building."


def buildToDirectory(args, directory, translation=False):

  buildDir = buildRootDir + directory
  if not os.path.exists(buildDir):
    os.makedirs(buildDir)

  subprocess.check_call([
    "html/build_html.sh",
    ("1" if args.fragment else "0"),
    ("1" if translation else "0")
  ])
  subprocess.check_call(["cp", "-r", "html/build/", buildDir])

  if args.pdf:
    subprocess.check_call(["pdf/build_pdf.sh"])
    subprocess.check_call([
      "cp",
      "pdf/build/wca-regulations-and-guidelines-2013.pdf",
      buildDir
    ])


def buildBranch(args, branchName, directory, translation=False):
  checkoutWCADocs(branchName)
  buildToDirectory(args, directory, translation)


def buildTranslation(args, lang):
  branchName = "translation-" + lang
  directory = "translations/" + lang + "/"
  translation = True

  if lang == "english":
    branchName = "official"
    directory = ""
    translation = False

  buildBranch(args, branchName, directory, translation=translation)


# Non-Build Actions


def archive(args):
  subprocess.check_call(["rm", "-rf", archiveFile])
  subprocess.check_call([
    "tar", "--exclude", ".DS_Store", "-zcf",
    archiveFile, buildRootDir
  ])


def upload(args):

  if not os.path.exists(upload_server_file):
    sys.stderr.write("Config file for server uploads does not exist.\n")
    sys.stderr.write("Please create one at " + upload_server_file + " using the template.\n")
    return

  with open(upload_server_file, "r") as fileHandle:
    upload_server = json.load(fileHandle)

  subprocess.check_call([
    "rsync",
    "-avz",
    buildRootDir] +
    ([archiveFile] if os.path.exists(archiveFile) else []) + [
    upload_server["sftp_path"]
  ])
  print "Done uploading to SFTP server."
  print "Visit " + upload_server["base_url"]
  print "Archive is at " + upload_server["base_url"] + archiveFile


def server(args):

  localURL = "http://localhost:8081/build/"
  if args.language in languages:
    localURL = localURL + "translations/" + args.language + "/"
  webbrowser.open(localURL)

  print "Serving " + buildRootDir + " at " + localURL
  print "Press Ctrl-C to halt."

  # This seems to work better than trying to call it from Python.
  subprocess.call(["python", "-m",  "SimpleHTTPServer", "8081"])


# Make the script work standalone.


if __name__ == "__main__":
    main()