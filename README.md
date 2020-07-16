# pinetmonitor
Pi Network Monitoring Tool

## What does it do?
The tool monitors ping to the given ip (default 8.8.8.8) and detects changes in the state ```(not )connected```. At change of state it retries for the configured number of times before marking the new state.

When the ping changes state from ```not connected``` to ```connected``` it sends a telegram message to the configured chat ids using the telegram access token that you have created.

## How to use?
1. Copy ```config-template.json``` to ```~/.pinetmonitorconfig.json```
2. Add the missing values to it.
3. Just run ```bin/pinetmonitor``` and it will start sending pings and monitoring the state.

## What is export?
You can export the ping data in form of ```.csv``` file. You can configure that as well.