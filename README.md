### What is Traces?
Traces is a Mac OS X daemon that continuously monitors and stores what you are doing on your computer. This includes clicks, keystrokes, app used, windows used, and regular screenshots. We are working on visualizing this data to make it easier to review your activity history to gain insights about your work patterns and make it easier to resume suspended work. The core logic of Traces is written in python so you can more easily add additional tracking modules and retool it to record on other operating systems.

This project was inspired by [Selfspy](https://github.com/gurgeh/selfspy) and [Burrito](https://github.com/pgbovine/burrito/).

### Installing Traces
We regularly compile Traces into a Mac OS X app. Go to the Release page to download the app.

Traces uses MongoDB, so make sure you [download](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/) MongoDB and start a MongoDB server before you start Traces. We are woking on making this process more automatic.

Since Traces takes regular screenshots it can fill your hard drive pretty quickly. We recommend setting your Data storage to an external drive, such as a USB key or SD card. Simply copy the `traces.cfg` file to the root of your desired data storage volume and mount the device onto your computer. Traces will recognize the volume and save its data there.

To install manually on OSX 10.10 you should do the following:

1. Clone the repository from Github (git clone git://github.com/activityhistory/traces) or click on the Download link on http://github.com/activityhistory/traces/ to get the latest Python source.

2. If you do not have xcode installed, install it now. Make sure you agree to its license agreement (e.g. by starting xcode.) Also make sure you have xcode command line tools installed.

3. Python should come with your OSX installation but if you if you do not already have it installed, install Python now.

4. Use your favorite package manager (or manual methods) to install the dependencies documented in the requirements.txt file. These mostly include the pyobjc frameworks that let our python code call OSX's Objecitve-C APIs.

5. Run `python setup.py py2app` to compile Traces into an OXS application (.app file).

Report any issues here:
https://github.com/activityhistory/traces/issues

#### Running on OS X
To use the full capabilities of Traces in OS X, you need to grant it Accessibility access. This lets it keep track of the applications and windows you use. You can grant this access in `System Preferences > Privacy > Accessibility`.
