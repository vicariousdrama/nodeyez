---
name: Nodeyez-Config Tool
title: NODEYEZ Configuration Tool
layout: default
---

# Nodeyez-Config

The Nodeyez-Config tool encompasses most of the configuration needs you may have with Nodeyez.  It can show you a list of all the services available, and allow you to drill down into the detailed configuration options.

## Installing the tool

If you installed Nodeyez using the [Quick Start]({% link _install_steps/0quickstart.md %}), then the tool was installed and may be run from the terminal.  If you are doing a manual install, then run this command to copy to the bin folder

```sh
sudo cp /home/nodeyez/nodeyez/scripts/nodeyez-config /usr/local/bin
```

## Launching the tool

To simply view settings, you should be able to run the tool as any user

```sh
nodeyez-config
```

But to make configuration changes, or start/stop services, you'll want to run it with sudo privileges

```sh
sudo nodeyez-config
```

## Main Menu

When you run the tool, you'll initially be presented with a menu

![sample image of nodeyez-config main menu](../images/nodeyez-config-main-menu.png)

Use arrow or other navigation keys to move through this list and press &lt;ENTER&gt; to confirm a selection.  Pressing &lt;ESC&gt; will back out of menu choices.

## Bitcoin Settings

Entering this choice will show the currently active profile for bitcoin calls, and let you manage the settings of all profiles.  

You will need to define settings for a profile to use Bitcoin panels.

The information you need to configure in Nodeyez for each Bitcoin Profile is
- address: The ip address or fully qualified domain name of the Bitcoin server accessible over rest for rpc calls. The default assumes running Nodeyez on the same machine as bitcoin. Note that if its a docker setup, you need to specify the IP address associated with that container.
- name: You can name profiles to tell them apart
- port: The port the server will listen for requests on. By default, this is port 8332, and is set as the `rpcport` line in bitcoin.conf
- rpcpassword: The password for accessing the bitcoin node. This will either be the same as the clear text value of the deprecated `rpcpassword` in the bitcoin.conf, or the password specified or returned when preparing the `rpcauth` line from the rpcauth.py script.
- rpcuser: This is the same value as the `rpcuser` in bitcoin.conf, or the user portion of the `rpcauth` line.
- useTor: For remote nodes, you can optionally enable calls over Tor. For internal network nodes, leave it as False.

While bitcoin.conf settings are outside of the scope of this project and there's many resources online, what you'll generally need to be familiar with is setting up the following

- rpcauth
- rpcallowip
- rpcbind
- rpcport

## LND Settings

Entering this choice will show the currently active profile for LND lightning calls, and let you manage the settings of all profiles.  

You will need to define settings for a profile to use Lightning panels.

The information you need to configure in Nodeyez for each Lightning Profile is
- address: The ip address or fully qualified domain name of the LND server. The default assumes running Nodeyez on the same machine as LND. Note that if its a docker setup, you need to specify the IP address associated with that container.
- macaroon: The hex representation of the macaroon granting authorization to the LND server.
- name: You can name profiles to tell them apart
- port: The port the server will listen for requests on. By default, this is port 10080 and coincides with the port specified in the `restlisten` line of lnd.conf
- useTor: For remote nodes, you can optionally enable calls over Tor. For internal network nodes, leave it as False.

While lnd.conf settings are outside of the scope of this project and there's many resources online, what you'll generally need to be familiar with is setting up the following

- rpclisten
- restlisten

## Service Listing

This option provides list of services that Nodeyez recognizes

![sample image of nodeyez-config services](../images/nodeyez-config-service-list.png)

For convenience, activated services are presented at the top with an 'on' indicator in the description field.

The title bar for the window provides an indication of what context you are running the configuration tool under. The tool should be run with effective root access to enable/disable services or start/stop them.  Similarly, either root or nodeyez group access if you want to make configuration changes.

## Service Options

Upon selecting a service, a list of choices specific to that service will appear.

![sample](../images/nodeyez-config-service-options.png)

The Configure option for viewing and setting properties for the script is only available for those services that have configuration settings.

If you are running the nodeyez-config tool with root privileges, then you'll see the Run on Bootup and Run Service options. Choosing them will toggle their state.

The Recent Logs option will report the most recent 20 lines of log entries which may be useful for diagnostics if something does not appear to be working as expected.

![sample service logs](../images/nodeyez-config-service-logs.png)

In the above example, the mempoolspace service had a connection error reaching a resource.  Where possible, services will continue working with the data they have, and update on the next attempt.

If the service is running, then you'll also be presented with the option to view the Status of the service.

![sample service status](../images/nodeyez-config-service-status.png)

## View Properties

When you choose to customize configuration settings for a service, you'll be presented with the properties that can be configured, and their current values.

![sample configuration of mempoolspace](../images/nodeyez-config-mempoolspace-options.png)

Property values are truncated if they are overly long to try to fit within the dialog window space.

Sensitive values such as passwords, authorization tokens and api keys will be treated as passwords and have their values "starred out".  The only way to view their cleartext value is to view the json configuration file directly.

Some configuration settings have nested options. In the example above, at the bottom of the list are choices to set the definitions of two different nested choices.

## View Nested Item

If the nested item is an array of multiple values, you'll see the listing of current entries.  

![sample view of nested entries for a property](../images/nodeyez-config-mempoolspace-blockSatRangeColors.png)

You may navigate to an entry to view details and modify, or choose the Add option if you want to make another definition.

When editing an item within a nested list, the configuration is similar to configuring properties.

![sample view of editing a nested item](../images/nodeyez-config-mempoolspace-blockSatRangeColors-item.png)

Here, there is an option at the bottom of the list that allows for deleting the item.

The title bar also provides for context of which item we are editing, and follows a JSONPath like descriptive format.

## Making Changes

If you press &lt;ENTER&gt; on a property, it will then present you with the option to modify its value.

The screen depicted will vary based on the property type.

Here is a common input for strings and numbers.  If the field is a sensitive field (passwords, authorization tokens and api keys), the value will be starred out.

![sam](../images/nodeyez-config-mempoolspace-blockSatRangeColors-item-edit.png)

The value will be prepulated with the current value for the property.

A description of the property is presented, and where applicable, information about the default value is given.

Validation rules are in place for any property that is a number (whole numbers or real), defined as a color, a boolean, or restricted to a list.

Make your changes, and confirm them by pressing &lt;ENTER&gt; or cancel by pressing &lt;ESC&gt; to go back.


---

[Home](../) | [Back to Running Services at Startup]({% link _install_steps/8runatstartup.md %})
