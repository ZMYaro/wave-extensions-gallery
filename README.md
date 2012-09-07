#Wave Extensions Gallery

This app is meant to be an index of and (in the case of gadgets) storage for wave extensions.  Users can sign in and favorite extensions.  Developers can add their extensions to the gallery.  Wave clients can pull gadgets and gadget data from the gallery.  Having a central source for extensions eliminates the need for wave clients to keep their own lists of gadgets.

(Note: This has not all been implemented, but it will be.)

--------

###Running the app locally (Linux)

####Getting dependencies
1. Download and install Git from http://git-scm.com/download or your package manager
2. Download and install Python from http://python.org/download or your package manager
3. Download and unzip (Linux) the Google App Engine SDK for Python from https://developers.google.com/appengine/downloads

####Getting the files
1. In a terminal, clone the repository: `git clone git@github.com:zmyaro/wave-extensions-gallery.git`

####Running the app
1. `cd path/to/wave-extensions-gallery`
2. `path/to/google_appengine/dev_appserver.py app`
3. The app should now be running locally, accessible at localhost:8080

--------

###Running the app locally (Windows, with GitHub)

####Getting dependencies
1. Download and install GitHub for Windows from http://windows.github.com
2. Download and install Python from http://python.org/download
3. Download and install the Google App Engine SDK for Python from https://developers.google.com/appengine/downloads

####Getting the files
1. Open GitHub for Windows and sign in with your GitHub account
2. Go to http://github.com/zmyaro/wave-extensions-gallery and sign in with the same account
3. Click the “Clone in Windows” button; GitHub for Windows should automatically download the files

####Running the app
1. Open Google App Engine Launcher (installed with the App Engine SDK)
2. If it is not already set, select to “Edit” → “Preferences...”, click the “Select...” button for “Python Path”, and locate python.exe (usually somewhere like C:\Python27)
3. Select “File” → “Add Existing Application...”, click “Browse...”, and navigate to “My Documents\GitHub\wave-extensions-gallery\app”
4. Select the newly-added project in App Engine Launcher and click the “Run” button on the toolbar at the top
5. The app should now be running locally, accessible at localhost:8080

--------

###Running the app locally without using Git

1. Go to http://github.com/zmyaro/wave-extensions-gallery
2. Click the ZIP button to download the current version as a ZIP file
3. Unzip the file you downloaded
4. Follow the above steps for your operating system, ignoring all Git-related instructions
5. On Windows, replace the file path in step 3 of “Running the app” with wherever you unzipped the files

**Note that using Git makes it much easier to keep your copy of the files up-to-date