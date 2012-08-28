#Wave Extensions Gallery

This app is meant to be an index of and (in the case of gadgets) storage* for wave extensions.  Users can sign in and favorite extensions.  Developers can add their extensions to the gallery.  Wave clients can pull gadgets and gadget data from the gallery.  Having a central source for extensions eliminates the need for wave clients to keep their own lists of

*storage not yet implemented

--------

##Dependencies for running locally

* Download and install git from http://git-scm.com/download (or your package manager)
* Clone the repository: `git clone git@github.com:zmyaro/wave-extensions-gallery.git`
* Download and install Python from http://python.org/download (or your package manager)
* Download and install (Windows/Mac) or unzip (Linux) the Google App Engine SDK for Python from https://developers.google.com/appengine/downloads

--------

##Running the app locally (Linux)

* Open a terminal
* `cd path/to/wave-extensions-gallery`
* `path/to/google_appengine/dev_appserver.py app`
* The app should now be running locally, accessible at localhost:8080
