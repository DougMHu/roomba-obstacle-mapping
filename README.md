# roomba-obstacle-mapping

roomba-obstacle-mapping is a Python library for obstacle mapping using an iRobot Create 2 in a living room. The living room can be optionally equipped with [Tmote-Skys][tmote] or [Estimotes][estimotes]. Only tested on Ubuntu.

It uses iRobot's [Python API][irobot] for controlling the Create 2. It also uses [Python's Turtle graphics][turtle] for path visualization.

(Optional) An accompanying iOS application for reading location from the Estimotes is available at [roomba-estimotes-localization][ios-app]. Accompanying Tmote broadcast code can be found at [contiki](https://github.com/DougMHu/contiki/tree/ee579).

## Ubuntu/OSX Installation Using pip

Open Terminal, navigate to this directory. Try:
```
$ python localization/trilateration.py
```

If you see import error messages, import the missing packages using [pip][pip-url]:
```
$ pip install package-name-here
```
Ignore other error messages... until after you finish Hardware Setup.

Then repeat for the following scripts:
* mqtt/mqtt_paho_subscribe.py
* visualization/turtle_roomba.py
* roomba/roomba.py
* mapping/mapping.py

## Hardware Setup
### Create 2 Setup
Plug in the Create 2. Try running iRobot's Create 2 GUI, following this [tutorial][irobot] if necessary:
```
$ sudo python roomba/Create2_TetheredDrive.py
```
If this works for you, and you're able to drive the Create 2 around with arrow keys, then you're in good shape.

Check what port the Create 2 is connected to using:
```
$ dmesg | grep tty
```
Then, open `roomba/roomba.py` and change the port variable accordingly. e.g.
```
port = "/dev/ttyUSB0"
```

### Optional
### Tmote Setup
To setup the Tmote receiver, make sure to [program the Tmote-Skys][tmote] and check they are receiving broadcasts.
Plug in the Tmote-Sky. Check what port it is connected to using `dmesg | grep tty`. Then, open `localization/measure_rssi.py` and change port variable accordingly.

### Estimote Setup
To setup the Estimote receiver, make sure your computer and your phone are connected to WiFi. Before running your iOS App, try:
```
$ python mqtt/mqtt_test.py
```
If you start receiving messages, then someone else is publishing to "your" topic :(
Else, you're in good shape. Just `Ctrl-C` a few times until the script halts.

If you received foreign messages, consider changing to a more unique topic name. First, [change the iOS App's topic][ios-app]. Then open `mqtt/mqtt_test.py` and change `topic_name` variable accordingly. Run the `mqtt_test.py` script again. If you are successful (no foreign messages), then open `mqtt/mqtt_paho_subscribe.py` and change the `topic_name` variable accordingly.

Start the iOS App on your phone, making sure it is [updating][ios-app]. Run the `mqtt_test.py` script again. You should start receiving your own location coordinates.

## Usage

Start by running a simulation:
```
$ python mapping/mapping_sim.py
```
This simulates the behavior you would expect to see as the Create 2 discovers the obstacles in your living room.

To run standalone Create 2 mapping, open `mapping/mapping.py` and set `sampling = False`. Change the `length` and `width` to reflect your room dimensions in millimeters. Then, with the laptop tethered to the Create 2, run:
```
$ sudo python mapping/mapping.py
```

### Optional
To run Create 2 mapping accompanied by Estimote sampling or Tmote sampling, open `mapping/mapping.py` and set the configuration variables to:
```
sampling = True
if (sampling):
	sampler = "Estimote"
```
or
```
sampling = True
if (sampling):
	sampler = "Tmote"
```
Then run:
```
$ sudo python mapping/mapping.py
```

## Authors

* Aashiq Ahmed (aashiqah@usc.edu)
* Shuai Chen (shuaic@usc.edu)
* Meha Deora (mdeora@usc.edu)
* Douglas Hu (douglamh@usc.edu)

[tmote]: http://www.eecs.harvard.edu/~konrad/projects/shimmer/references/tmote-sky-datasheet.pdf
[estimotes]: http://estimote.com/
[irobot]: http://www.irobotweb.com/~/media/MainSite/PDFs/About/STEM/Create/Python_Tethered_Driving.pdf
[turtle]: https://docs.python.org/2/library/turtle.html
[pip-url]: https://pip.pypa.io/en/stable/installing/
[ios-app]: https://github.com/DougMHu/roomba-estimotes-localization
