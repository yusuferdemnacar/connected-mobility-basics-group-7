# Notes for Assignment 1 Review 1
Date: _14.05.2024_
Participants:  
- Yusuf Erdem Nacar
- Dan Bachar
- Ja

## What to Model
Ad-hoc network for simple messaging.

## Use Cases
### Use Case 1
Ad-hoc network message passing against censorship in dictatorships.

### Use Case 2
Internet infrastructure not sufficient/not present due some reason
  - Earthquake/Fire
      - Dynamics of mobility of people might change - less than ideal to model.
  - Cellular & LRZ is down due to some attack, ad-hoc comms as a fallback
      - Would people continue with their usual routines?

## Movement patterns
Most movements happen once every 1.5h or 2.25h due to lectures beginning and ending, some random movements due to people studying in MI

### READ
* TODO: What are the different movement models that we have? (e.g. Levy walk)

## What to Measure
* Range
* Peer density
* Latency
* Throughput (Goodput?)
* BLE vs WLAN?

## Routing
* TODO: See what kind of message relaying protocols that the simulator supports
* Gut feeling: flood is the easiest
* Options:
    * RPL
    * AODV
    * BATMAN
    * Flood
        * If we go with flood: examine how fanout setting effects performance (how many peers does a node forward a message to)
    * More?


# Presentation
* Present use case
* present model
* What mdodel we want to use for the mobility
* How do we structure maps
* Metrics (Optional)