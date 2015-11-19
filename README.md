### What is Traces?
Traces is a Mac OS X daemon that continuously monitors and records your computer activity. This includes tracking clicks, keystrokes, apps, windows, and taking regular screenshots. We are currently developing visualizations of this data to make it easier to see work patterns and resume suspended activities. Traces is written in python so you can easily add additional modules.

This project was inspired by [Selfspy](https://github.com/gurgeh/selfspy) and [Burrito](https://github.com/pgbovine/burrito/).

### Installing Traces
We regularly compile Traces into a Mac OS X app. Go to the [Releases](https://github.com/activityhistory/traces/releases) page to download the most recent release.

Traces takes regular screenshots and can fill your hard drive pretty quickly. We recommend setting your Data storage to an external drive, such as a USB key or SD card. To do this, copy the `traces.cfg` file to the root of your desired data storage volume and mount the device onto your computer. The next time you start Traces, it will recognize the volume and save its data there.

To install Traces manually on OSX you should:

1. Clone the repository from Github (git clone git://github.com/activityhistory/traces) or click on the Download link on http://github.com/activityhistory/traces/ to get the latest Python source.

2. Install xcode if you have not done so already. Make sure you agree to its license agreement (i.e. by starting xcode). Also make sure you have xcode command line tools installed.

3. Python should come with your OSX installation but if you do not already have it installed, install Python now.

4. Use your favorite package manager (or manual methods) to install the dependencies documented in the requirements-osx.txt file. These mostly include the pyobjc frameworks that let our python code call OSX's Objecitve-C APIs.

5. Run `python setup.py py2app` to compile Traces into an OXS application (.app file).

Report any issues here:
https://github.com/activityhistory/traces/issues

#### Running on OS X
To use the full capabilities of Traces in OSX, you need to grant it Accessibility access. This lets it keep track your keystrokes, applications, and windows. You can grant Accessibility access in `System Preferences > Privacy > Accessibility`.
