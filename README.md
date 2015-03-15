# Waage
Capture Data from your bathroom scales and watch the results on your own web server. Make yourself independent of the internet based Soehnle server.
This works for my Soehnle 63339. This is a cheapish model (at least in DE) that only captures your weight but not any other fancy stuff such as body fat.

## Why?

### The problem:
The scales usually talk to a server in the internet to tell it my weight. Then I can log on to the Soehnlt web page and check on my progress. Each member of the family has to register seperately in order to get access to their data.
The export function only works by sending Excel files via Email.

The scales are ok. They don't look very techie - just like bathroom scales. But the internet service is not exactly what I want. This is why I needed to do some reverse engineering....

### The solution:
The scales only use http to talk to the server. It was quite easy to intercept the communication and find out how the weight is sent to the webserver. 

## How?
This is one way to do it. Your environment is most likely completely different - maybe you find some even easier solutions.

You need:
* a DNS server for directing requests that are supposed to reach bridge1.soehnle.de to your own web server
* a web server listening on port 80
* the cgi *dataservice* that is called when the scales want to contact http://bridge1.soehnle.de/devicedataservice/dataservice. *dataservice* generates a log file that contains a timestamp and the relevant data that the scales sent off. The scales send of several different messages to the server. Sometimes this is unrelated to the actual usage of the scales. I have no idea what information is sent to the server. The cgi *dataservice* just replies with the same codes as the original.
* the cgi *waage-tabelle-aktualisieren.py* that is called by yourself. It reads the output of *dataservice*, builds a web page  and calls gnuplot to generate some graphics. Just adapt it for your own needs.

