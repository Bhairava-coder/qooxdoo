#!/usr/bin/env python

import sys, re, os, optparse

# reconfigure path to import own modules from modules subfolder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "modules"))

import config, tokenizer, loader, tokencompiler, api, tree, treegenerator, settings, resources, filetool, stringcompress, extendedoption, treecompiler






def getparser():
  parser = optparse.OptionParser("usage: %prog [options]", option_class=extendedoption.ExtendedOption)


  #################################################################################
  # GENERAL
  #################################################################################

  # From/To File
  parser.add_option("--from-file", dest="fromFile", metavar="FILENAME", help="Read options from FILENAME.")
  parser.add_option("--export-to-file", dest="exportToFile", metavar="FILENAME", help="Store options to FILENAME.")

  # Directories (Lists, Match using index)
  parser.add_option("--script-input", action="extend", dest="scriptInput", metavar="DIRECTORY", type="string", default=[], help="Define a script input directory.")
  parser.add_option("--script-encoding", action="extend", dest="scriptEncoding", metavar="ENCODING", type="string", default=[], help="Define the encoding for a script input directory.")
  parser.add_option("--source-script-path", action="extend", dest="sourceScriptPath", metavar="PATH", type="string", default=[], help="Define a script path for the source version.")
  parser.add_option("--resource-input", action="extend", dest="resourceInput", metavar="DIRECTORY", type="string", default=[], help="Define a resource input directory.")
  parser.add_option("--resource-output", action="extend", dest="resourceOutput", metavar="DIRECTORY", type="string", default=[], help="Define a resource output directory.")

  # Available Actions
  parser.add_option("--generate-compiled-script", action="store_true", dest="generateCompiledScript", default=False, help="Compile source files.")
  parser.add_option("--generate-source-script", action="store_true", dest="generateSourceScript", default=False, help="Generate source version.")
  parser.add_option("--generate-api-documentation", action="store_true", dest="generateApiDocumentation", default=False, help="Generate API documentation.")
  parser.add_option("--copy-resources", action="store_true", dest="copyResources", default=False, help="Copy resource files.")

  # Debug Actions
  parser.add_option("--store-tokens", action="store_true", dest="storeTokens", default=False, help="Store tokenized content of source files. (Debugging)")
  parser.add_option("--store-tree", action="store_true", dest="storeTree", default=False, help="Store tree content of source files. (Debugging)")
  parser.add_option("--print-files", action="store_true", dest="printFiles", default=False, help="Output known files. (Debugging)")
  parser.add_option("--print-modules", action="store_true", dest="printModules", default=False, help="Output known modules. (Debugging)")
  parser.add_option("--print-files-without-modules", action="store_true", dest="printFilesWithoutModules", default=False, help="Output files which have no module connection. (Debugging)")
  parser.add_option("--print-includes", action="store_true", dest="printIncludes", default=False, help="Output sorted file list. (Debugging)")
  parser.add_option("--print-dependencies", action="store_true", dest="printDeps", default=False, help="Output dependencies of files. (Debugging)")

  # Output files
  parser.add_option("--source-script-file", dest="sourceScriptFile", metavar="FILENAME", help="Name of output file from source build process.")
  parser.add_option("--compiled-script-file", dest="compiledScriptFile", metavar="FILENAME", help="Name of output file from compiler.")
  parser.add_option("--api-documentation-json-file", dest="apiDocumentationJsonFile", metavar="FILENAME", help="Name of JSON API file.")
  parser.add_option("--api-documentation-xml-file", dest="apiDocumentationXmlFile", metavar="FILENAME", help="Name of XML API file.")
  parser.add_option("--settings-script-file", dest="settingsScriptFile", metavar="FILENAME", help="Name of settings script file.")

  # Encoding
  parser.add_option("--script-output-encoding", dest="scriptOutputEncoding", default="utf-8", metavar="ENCODING", help="Defines the encoding used for script output files.")
  parser.add_option("--xml-output-encoding", dest="xmlOutputEncoding", default="utf-8", metavar="ENCODING", help="Defines the encoding used for XML output files.")



  #################################################################################
  # OPTIONS
  #################################################################################

  # General options
  parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=False, help="Quiet output mode.")
  parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Verbose output mode.")
  parser.add_option("-d", "--debug", action="store_true", dest="enableDebug", help="Enable debug mode.")

  # Options for source and compiled version
  parser.add_option("--define-runtime-setting", action="append", dest="defineRuntimeSetting", metavar="NAMESPACE.KEY:VALUE", default=[], help="Define a setting.")
  parser.add_option("--add-new-lines", action="store_true", dest="addNewLines", default=False, help="Keep newlines in compiled files.")

  # Options for compiled version
  parser.add_option("--add-file-ids", action="store_true", dest="addFileIds", default=False, help="Add file IDs to compiled output.")
  parser.add_option("--compress-strings", action="store_true", dest="compressStrings", default=False, help="Compress strings. (ALPHA)")
  parser.add_option("--use-token-compiler", action="store_true", dest="useTokenCompiler", default=False, help="Use old token compiler instead of new tree compiler. (ALPHA)")

  # Options for resource copying
  parser.add_option("--override-resource-output", action="append", dest="overrideResourceOutput", metavar="CLASSNAME.ID:DIRECTORY", default=[], help="Define a resource input directory.")

  # Options for token/tree storage
  parser.add_option("--token-output-directory", dest="tokenOutputDirectory", metavar="DIRECTORY", help="Define output directory for tokenizer result of the incoming JavaScript files. (Debugging)")
  parser.add_option("--tree-output-directory", dest="treeOutputDirectory", metavar="DIRECTORY", help="Define output directory for generated tree of the incoming JavaScript files. (Debugging)")

  # Cache Directory
  parser.add_option("--cache-directory", dest="cacheDirectory", metavar="DIRECTORY", help="If this is defined the loader trys to use cache to optimize the performance.")




  #################################################################################
  # INCLUDE/EXCLUDE
  #################################################################################

  # Include/Exclude
  parser.add_option("-i", "--include", action="extend", dest="includeWithDeps", metavar="ID", type="string", default=[], help="Include ID")
  parser.add_option("-e", "--exclude", action="extend", dest="excludeWithDeps", metavar="ID", type="string", default=[], help="Exclude ID")
  parser.add_option("--include-without-dependencies", action="extend", dest="includeWithoutDeps", metavar="ID", type="string", default=[], help="Include ID")
  parser.add_option("--exclude-without-dependencies", action="extend", dest="excludeWithoutDeps", metavar="ID", type="string", default=[], help="Exclude ID")

  # Include/Exclude options
  parser.add_option("--disable-auto-dependencies", action="store_false", dest="enableAutoDependencies", default=True, help="Disable detection of dependencies.")

  return parser






def argparser(cmdlineargs):

  # Parse arguments
  (options, args) = getparser().parse_args(cmdlineargs)

  # Export to file
  if options.exportToFile != None:
    print
    print "  EXPORTING:"
    print "----------------------------------------------------------------------------"

    print " * Translating options..."

    optionString = "# Exported configuration from build.py\n\n"
    ignoreValue = True
    lastWasKey = False

    for arg in cmdlineargs:
      if arg == "--export-to-file":
        ignoreValue = True

      elif arg.startswith("--"):
        if lastWasKey:
          optionString += "\n"

        optionString += arg[2:]
        ignoreValue = False
        lastWasKey = True

      elif arg.startswith("-"):
        print "   * Couldn't export short argument: %s" % arg
        optionString += "\n# Ignored short argument %s\n" % arg
        ignoreValue = True

      elif not ignoreValue:
        optionString += " = %s\n" % arg
        ignoreValue = True
        lastWasKey = False



    print " * Export to file: %s" % options.exportToFile
    filetool.save(options.exportToFile, optionString)

    sys.exit(0)

  # Read from file
  elif options.fromFile != None:

    print
    print "  INITIALIZATION:"
    print "----------------------------------------------------------------------------"

    print "  * Reading configuration..."

    # Convert file content into arguments
    fileargs = {}
    fileargpos = 0
    fileargid = "default"
    currentfileargs = []
    fileargs[fileargid] = currentfileargs

    alternativeFormatBegin = re.compile("\s*\[\s*")
    alternativeFormatEnd = re.compile("\s*\]\s*=\s*")
    emptyLine = re.compile("^\s*$")

    for line in file(options.fromFile).read().split("\n"):
      line = line.strip()

      if emptyLine.match(line) or line.startswith("#") or line.startswith("//"):
        continue

      # Translating...
      line = alternativeFormatBegin.sub(" = ", line)
      line = alternativeFormatEnd.sub(":", line)

      # Splitting line
      line = line.split("=")

      # Extract key element
      key = line.pop(0).strip()

      # Separate packages
      if key == "package":
        fileargpos += 1
        fileargid = line[0].strip()

        print "    - Found package: %s" % fileargid

        currentfileargs = []
        fileargs[fileargid] = currentfileargs
        continue

      currentfileargs.append("--%s" % key)

      if len(line) > 0:
        value = line[0].strip()
        currentfileargs.append(value)

    # Parse
    defaultargs = fileargs["default"]

    if len(fileargs) > 1:
      (fileDb, moduleDb) = load(getparser().parse_args(defaultargs)[0])

      for filearg in fileargs:
        if filearg == "default":
          continue

        print
        print
        print "**************************** Next Package **********************************"
        print "PACKAGE: %s" % filearg

        combinedargs = []
        combinedargs.extend(defaultargs)
        combinedargs.extend(fileargs[filearg])

        options = getparser().parse_args(combinedargs)[0]
        execute(fileDb, moduleDb, options, filearg)

    else:
      options = getparser().parse_args(defaultargs)[0]
      (fileDb, moduleDb) = load(options)
      execute(fileDb, moduleDb, options)

  else:
    print
    print "  INITIALIZATION:"
    print "----------------------------------------------------------------------------"

    print "  * Processing arguments..."

    (fileDb, moduleDb) = load(options)
    execute(fileDb, moduleDb, options)







def main():
  if len(sys.argv[1:]) == 0:
    basename = os.path.basename(sys.argv[0])
    print "usage: %s [options]" % basename
    print "Try '%s -h' or '%s --help' to show the help message." % (basename, basename)
    sys.exit(1)

  argparser(sys.argv[1:])






def load(options):

  ######################################################################
  #  SOURCE LOADER
  ######################################################################

  print
  print "  SOURCE LOADER:"
  print "----------------------------------------------------------------------------"

  if options.scriptInput == None or len(options.scriptInput) == 0:
    basename = os.path.basename(sys.argv[0])
    print "You must define at least one script input directory!"
    print "usage: %s [options]" % basename
    print "Try '%s -h' or '%s --help' to show the help message." % (basename, basename)
    sys.exit(1)

  if options.verbose:
    print "  * Loading JavaScript files... "
  else:
    print "  * Loading JavaScript files: ",

  (fileDb, moduleDb) = loader.indexScriptInput(options)

  if not options.verbose:
    print

  print "  * Found %s JavaScript files" % len(fileDb)





  ######################################################################
  #  DEBUG OUTPUT JOBS
  ######################################################################

  if options.printFiles:
    print
    print "  OUTPUT OF KNOWN FILES:"
    print "----------------------------------------------------------------------------"
    print "  * These are all known files:"
    for fileEntry in fileDb:
      print "    - %s (%s)" % (fileEntry, fileDb[fileEntry]["path"])

  if options.printModules:
    print
    print "  OUTPUT OF KNOWN MODULES:"
    print "----------------------------------------------------------------------------"
    print "  * These are all known modules:"
    for moduleEntry in moduleDb:
      print "    * %s" % moduleEntry
      for fileEntry in moduleDb[moduleEntry]:
        print "      - %s" % fileEntry

  if options.printFilesWithoutModules:
    print
    print "  OUTPUT OF FILES WHICH HAVE NO MODULE CONNECTION:"
    print "----------------------------------------------------------------------------"
    print "  * These are all files without a module connection:"
    for fileEntry in fileDb:
      fileFound = False

      for moduleEntry in moduleDb:
        for moduleFile in moduleDb[moduleEntry]:
          if moduleFile == fileEntry:
            fileFound = True
            break

      if not fileFound:
        print "    - %s" % fileEntry




  ######################################################################
  #  DETECTION OF AUTO DEPENDENCIES
  ######################################################################

  if options.enableAutoDependencies:
    print
    print "  DETECTION OF AUTO DEPENDENCIES:"
    print "----------------------------------------------------------------------------"

    print "  * Collecting IDs..."

    knownIds = []
    depCounter = 0

    for fileEntry in fileDb:
      knownIds.append(fileEntry)

    if options.verbose:
      print "  * Detecting dependencies..."
    else:
      print "  * Detecting dependencies: ",

    for fileEntry in fileDb:
      if options.verbose:
        print "    * %s" % fileEntry
      else:
        sys.stdout.write(".")
        sys.stdout.flush()

      hasMessage = False

      fileTokens = fileDb[fileEntry]["tokens"]
      fileDeps = []

      assembledName = ""

      for token in fileTokens:
        if token["type"] == "name" or token["type"] == "builtin":
          if assembledName == "":
            assembledName = token["source"]
          else:
            assembledName += ".%s" % token["source"]

          if assembledName in knownIds:
            if assembledName != fileEntry and not assembledName in fileDeps:
              fileDeps.append(assembledName)

            assembledName = ""

        elif not (token["type"] == "token" and token["source"] == "."):
          if assembledName != "":
            assembledName = ""

          if token["type"] == "string" and token["source"] in knownIds and token["source"] != fileEntry and not token["source"] in fileDeps:
            fileDeps.append(token["source"])

      # Updating lists...
      optionalDeps = fileDb[fileEntry]["optionalDeps"]
      loadtimeDeps = fileDb[fileEntry]["loadtimeDeps"]
      runtimeDeps = fileDb[fileEntry]["runtimeDeps"]

      # Removing optional deps from list
      for dep in optionalDeps:
        if dep in fileDeps:
          fileDeps.remove(dep)

      # Checking loadtime dependencies
      for dep in loadtimeDeps:
        if not dep in fileDeps:
          if not hasMessage and not options.verbose:
            hasMessage = True
            print

          print "    * Could not confirm #require(%s) in %s!" % (dep, fileEntry)

      # Checking runtime dependencies
      for dep in runtimeDeps:
        if not dep in fileDeps:
          if not hasMessage and not options.verbose:
            hasMessage = True
            print

          print "    * Could not confirm #use(%s) in %s!" % (dep, fileEntry)

      # Adding new content to runtime dependencies
      for dep in fileDeps:
        if not dep in runtimeDeps and not dep in loadtimeDeps:
          if options.verbose:
            if not hasMessage and not options.verbose:
              hasMessage = True
              print

            print "    * Add dependency: %s" % dep

          runtimeDeps.append(dep)
          depCounter += 1


    if not hasMessage and not options.verbose:
      print

    print "  * Added %s dependencies" % depCounter

  return fileDb, moduleDb







def execute(fileDb, moduleDb, options, pkgid=""):

  additionalOutput = []


  ######################################################################
  #  SORT OF INCLUDE LIST
  ######################################################################

  print
  print "  SORT OF INCLUDE LIST:"
  print "----------------------------------------------------------------------------"

  if options.verbose:
    print "  * Include (with dependencies): %s" % options.includeWithDeps
    print "  * Include (without dependencies): %s" % options.includeWithoutDeps
    print "  * Exclude (with dependencies): %s" % options.excludeWithDeps
    print "  * Exclude (without dependencies): %s" % options.excludeWithoutDeps

  print "  * Sorting classes..."

  sortedIncludeList = loader.getSortedList(options, fileDb, moduleDb)

  print "  * Arranged %s classes" % len(sortedIncludeList)

  if options.printIncludes:
    print
    print "  PRINT OF INCLUDE ORDER:"
    print "----------------------------------------------------------------------------"
    print "  * The files will be included in this order:"
    for fileEntry in sortedIncludeList:
      print "    - %s" % fileEntry

  if options.printDeps:
    print
    print "  OUTPUT OF DEPENDENCIES:"
    print "----------------------------------------------------------------------------"
    print "  * These are all included files with their dependencies:"
    for fileEntry in sortedIncludeList:
      print "    - %s" % fileEntry
      if len(fileDb[fileEntry]["loadtimeDeps"]) > 0:
        print "      - Loadtime: "
        for depEntry in fileDb[fileEntry]["loadtimeDeps"]:
          print "        - %s" % depEntry

      if len(fileDb[fileEntry]["afterDeps"]) > 0:
        print "      - After: "
        for depEntry in fileDb[fileEntry]["afterDeps"]:
          print "        - %s" % depEntry

      if len(fileDb[fileEntry]["runtimeDeps"]) > 0:
        print "      - Runtime: "
        for depEntry in fileDb[fileEntry]["runtimeDeps"]:
          print "        - %s" % depEntry

      if len(fileDb[fileEntry]["beforeDeps"]) > 0:
        print "      - Before: "
        for depEntry in fileDb[fileEntry]["beforeDeps"]:
          print "        - %s" % depEntry

      if len(fileDb[fileEntry]["optionalDeps"]) > 0:
        print "      - Optional: "
        for depEntry in fileDb[fileEntry]["optionalDeps"]:
          print "        - %s" % depEntry




  ######################################################################
  #  STRING COMPRESSION
  ######################################################################

  if options.compressStrings:
    print
    print "  STRING COMPRESSION:"
    print "----------------------------------------------------------------------------"

    print "  * Searching for strings..."

    stringMap = {}

    for fileId in sortedIncludeList:
      fileEntry = fileDb[fileId]
      fileTree = fileEntry["tree"]

      stringcompress.search(fileTree, stringMap, options.verbose)

    counter = 0
    for value in stringMap:
      counter += stringMap[value]

    print "  * Found %s strings, used %s times" % (len(stringMap), counter)

    print "  * Sorting strings..."
    stringList = stringcompress.sort(stringMap)
    print stringList

    print "  * Replacing strings..."
    for fileId in sortedIncludeList:
      stringcompress.replace(fileDb[fileId]["tree"], stringList, "$", options.verbose)

    print "  * Generating replacement object..."
    additionalOutput.append(stringcompress.array(stringList))








  ######################################################################
  #  TOKEN STORAGE
  ######################################################################

  if options.storeTokens:
    print
    print "  TOKEN STORAGE:"
    print "----------------------------------------------------------------------------"

    if options.tokenOutputDirectory == None:
      print "    * You must define the token output directory!"
      sys.exit(1)

    if options.verbose:
      print "  * Storing tokens..."
    else:
      print "  * Storing tokens: ",

    for fileId in sortedIncludeList:
      tokenString = tokenizer.convertTokensToString(fileDb[fileId]["tokens"])

      if options.verbose:
        print "    * writing tokens for %s (%s KB)..." % (fileIdm, len(tokenString) / 1000.0)
      else:
        sys.stdout.write(".")
        sys.stdout.flush()

      filetool.save(os.path.join(filetool.normalize(options.tokenOutputDirectory), fileId + config.TOKENEXT), tokenString)

    if not options.verbose:
      print




  ######################################################################
  #  TREE STORAGE
  ######################################################################

  if options.storeTree:
    print
    print "  TREE STORAGE:"
    print "----------------------------------------------------------------------------"

    if options.treeOutputDirectory == None:
      print "    * You must define the tree output directory!"
      sys.exit(1)

    if options.verbose:
      print "  * Storing tree..."
    else:
      print "  * Storing tree: ",

    for fileId in sortedIncludeList:
      treeString = "<?xml version=\"1.0\" encoding=\"" + options.xmlOutputEncoding + "\"?>\n" + tree.nodeToXmlString(fileDb[fileId]["tree"])

      if options.verbose:
        print "    * writing tree for %s (%s KB)..." % (fileId, len(treeString) / 1000.0)
      else:
        sys.stdout.write(".")
        sys.stdout.flush()

      filetool.save(os.path.join(filetool.normalize(options.treeOutputDirectory), fileId + config.XMLEXT), treeString)

    if not options.verbose:
      print



  ######################################################################
  #  GENERATION OF API
  ######################################################################

  if options.generateApiDocumentation:
    print
    print "  GENERATION OF API:"
    print "----------------------------------------------------------------------------"

    if options.apiDocumentationJsonFile == None and options.apiDocumentationXmlFile == None:
      print "    * You must define one of JSON or XML API documentation file!"

    docTree = None

    print "  * Generating API tree..."

    for fileId in sortedIncludeList:
      if options.verbose:
        print "  - %s" % fileId

      docTree = api.createDoc(fileDb[fileId]["tree"], docTree)

    if docTree:
      print "  * Finalising tree..."
      api.postWorkPackage(docTree, docTree)

    if options.apiDocumentationXmlFile != None:
      print "  * Writing XML API file to %s" % options.apiDocumentationXmlFile

      xmlContent = "<?xml version=\"1.0\" encoding=\"" + options.xmlOutputEncoding + "\"?>\n"

      if options.addNewLines:
        xmlContent += "\n" + tree.nodeToXmlString(docTree)
      else:
        xmlContent += tree.nodeToXmlString(docTree, "", "", "")

      filetool.save(options.apiDocumentationXmlFile, xmlContent, options.xmlOutputEncoding)

    if options.apiDocumentationJsonFile != None:
      print "  * Writing JSON API file to %s" % options.apiDocumentationJsonFile

      if options.addNewLines:
        jsonContent = tree.nodeToJsonString(docTree)
      else:
        jsonContent = tree.nodeToJsonString(docTree, "", "", "")

      filetool.save(options.apiDocumentationJsonFile, jsonContent, options.scriptOutputEncoding)





  ######################################################################
  #  CREATE COPY OF RESOURCES
  ######################################################################

  if options.copyResources:

    print
    print "  CREATE COPY OF RESOURCES:"
    print "----------------------------------------------------------------------------"

    resources.copy(options, sortedIncludeList, fileDb)






  ######################################################################
  #  GENERATION OF SETTINGS
  ######################################################################

  if options.generateSourceScript or options.generateCompiledScript:
    print
    print "  GENERATION OF SETTINGS:"
    print "----------------------------------------------------------------------------"

    print "  * Processing input data..."
    settingsStr = settings.generate(options)

    if options.settingsScriptFile:
      print "   * Saving settings to %s" % options.settingsScriptFile
      filetool.save(options.settingsScriptFile, settingsStr)

      # clear settings for build and source
      settingsStr = ""





  ######################################################################
  #  GENERATION OF SOURCE VERSION
  ######################################################################

  if options.generateSourceScript:
    print
    print "  GENERATION OF SOURCE SCRIPT:"
    print "----------------------------------------------------------------------------"

    if options.sourceScriptFile == None:
      print "    * You must define the source script file!"
      sys.exit(1)

    else:
      options.sourceScriptFile = os.path.normpath(options.sourceScriptFile)

    print "  * Generating includer..."

    sourceOutput = settingsStr

    if sourceOutput != "" and options.addNewLines:
      settingsStr += "\n"

    if options.addNewLines:
      for fileId in sortedIncludeList:
        if fileDb[fileId]["sourceScriptPath"] == None:
          print "  * Missing source path definition for script input %s. Could not create source script file!" % fileDb[fileId]["scriptInput"]
          sys.exit(1)

        sourceOutput += 'document.write(\'<script type="text/javascript" src="%s%s"></script>\');\n' % (os.path.join(fileDb[fileId]["sourceScriptPath"], fileDb[fileId]["pathId"].replace(".", os.sep)), config.JSEXT)

    else:
      includeCode = ""
      for fileId in sortedIncludeList:
        if fileDb[fileId]["sourceScriptPath"] == None:
          print "  * Missing source path definition for script input %s. Could not create source script file!" % fileDb[fileId]["scriptInput"]
          sys.exit(1)

        includeCode += '<script type="text/javascript" src="%s%s"></script>' % (os.path.join(fileDb[fileId]["sourceScriptPath"], fileDb[fileId]["pathId"].replace(".", os.sep)), config.JSEXT)
      sourceOutput += "document.write('%s');" % includeCode

    print "  * Saving includer output as %s..." % options.sourceScriptFile
    filetool.save(options.sourceScriptFile, sourceOutput, options.scriptOutputEncoding)






  ######################################################################
  #  GENERATION OF COMPILED VERSION
  ######################################################################

  if options.generateCompiledScript:
    print
    print "  GENERATION OF COMPILED SCRIPT:"
    print "----------------------------------------------------------------------------"

    compiledOutput = settingsStr + "".join(additionalOutput)

    if options.compiledScriptFile == None:
      print "    * You must define the compiled script file!"
      sys.exit(1)

    if options.useTokenCompiler:
      if options.verbose:
        print "  * Compiling tokens..."
      else:
        print "  * Compiling tokens: ",
    else:
      if options.verbose:
        print "  * Compiling tree..."
      else:
        print "  * Compiling tree: ",

    for fileId in sortedIncludeList:
      if options.verbose:
        print "    - %s" % fileId
      else:
        sys.stdout.write(".")
        sys.stdout.flush()

      if options.useTokenCompiler:
        compiledFileContent = tokencompiler.compile(fileDb[fileId]["tokens"], options.addNewLines, options.enableDebug)
      else:
        compiledFileContent = treecompiler.compile(fileDb[fileId]["tree"], options.addNewLines, options.enableDebug)

      if options.addFileIds:
        compiledOutput += "/* ID: " + fileId + " */\n" + compiledFileContent + "\n"
      else:
        compiledOutput += compiledFileContent

      if not compiledOutput.endswith(";"):
        compiledOutput += ";"

    if not options.verbose:
      print

    print "  * Saving compiled output as %s..." % options.compiledScriptFile
    filetool.save(options.compiledScriptFile, compiledOutput, options.scriptOutputEncoding)







######################################################################
#  MAIN LOOP
######################################################################

if __name__ == '__main__':
  try:
    main()

  except KeyboardInterrupt:
    print
    print "  * Keyboard Interrupt"
    sys.exit(1)
