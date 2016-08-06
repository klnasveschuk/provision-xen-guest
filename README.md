# provision-xen-guest
Provisions XenServer guest from templates, create Cobbler systems ready for PXE boot
This uses several systems
Cobbler templates are used build PXE boot files and build the systems using Kickstart and Preseed 
Xe commands use Xenserver templates to provision resources on the Xenserver host
DHCP on the Cobbler host provides the initial PXE files, install Yum repo/Apt source
DNS provision IPs, names through a standalone name server
