[app]
# title of your application
title = poi_catch
# project directory. the general assumption is that project_dir is the parent directory
# of input_file
project_dir = .
# source file path
input_file = D:\Documents\py_project\poi_catch\poi_catch\poi_catch.py
# directory where exec is stored
exec_directory = .
# path to .pyproject project file
project_file = poi_catch.pyproject
# application icon
icon = D:\Documents\py_project\poi_catch\poi_catch\icons\poi_catch.ico

[python]
# python path
python_path = D:\Documents\py_project\poi_catch\venv\Scripts\python.exe
# python packages to install
# ordered-set = increase compile time performance of nuitka packaging
# zstandard = provides final executable size optimization
packages = Nuitka==2.1
# buildozer = for deploying Android application
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]
# comma separated path to qml files required
# normally all the qml files required by the project are added automatically
qml_files = ApiKeyConfigPage.qml,Pagination.qml,main.qml
# excluded qml plugin binaries
excluded_qml_plugins = QtCharts,QtQuick3D,QtSensors,QtTest,QtWebEngine
# qt modules used. comma separated
modules = QmlModels,Qml,Core,QuickTemplates2,Gui,OpenGL,Quick,Network,QuickControls2
# qt plugins used by the application
plugins = platforminputcontexts,imageformats,platforms/darwin,generic,iconengines,egldeviceintegrations,accessiblebridge,xcbglintegrations,platforms,scenegraph,platformthemes,qmltooling

[android]
# path to pyside wheel
wheel_pyside = 
# path to shiboken wheel
wheel_shiboken = 
# plugins to be copied to libs folder of the packaged application. comma separated
plugins = 

[nuitka]
# usage description for permissions requested by the app as found in the info.plist file
# of the app bundle
# eg = extra_args = --show-modules --follow-stdlib --standalone
macos.permissions = 
# (str) specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations --windows-disable-console --include-data-files=qtquickcontrols2.conf=qtquickcontrols2.conf

[buildozer]
# build mode
# possible options = [release, debug]
# release creates an aab, while debug creates an apk
mode = debug
# contrains path to pyside6 and shiboken6 recipe dir
recipe_dir = 
# path to extra qt android jars to be loaded by the application
jars_dir = 
# if empty uses default ndk path downloaded by buildozer
ndk_path = 
# if empty uses default sdk path downloaded by buildozer
sdk_path = 
# other libraries to be loaded. comma separated.
# loaded at app startup
local_libs = 
# architecture of deployed platform
# possible values = ["aarch64", "armv7a", "i686", "x86_64"]
arch = 

