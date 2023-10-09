# spaceAPI

![spacewalk](https://github.com/paulosgf/spaceAPI/assets/25103947/3f135cdf-0b05-4eee-bad7-f04bb27d5139)

Python support scripts for Linux DevOps server updates via Spacewalk Platform.
These scripts will automatate the inteire process by creating a new channel clone, subscribing all systems divided by enviroment.
If successful, these systems will be removed from the old clones, and then these clones will be removed as well.
Finally, the updates followed by reboot will be scheduled on the chosen date.

This API only supports python 2.x and this project was completed by community in the year 2020, then being taken over by Oracle Inc through of Oracle Linux Manager project.

References

Red Hat Satellite XML-RPC API reference
https://access.redhat.com/documentation/en-us/red_hat_satellite/5.8/html/api_guide/index

Oracle Linux Manager
https://docs.oracle.com/en/operating-systems/oracle-linux-manager/index.html
 
Spacewalk
https://spacewalkproject.github.io/

