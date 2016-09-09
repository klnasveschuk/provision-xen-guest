# provision-xen-guest
Provisions XenServer (XenServer 6/7) guest from templates, create Cobbler systems ready for PXE boot
This uses several systems:
- Cobbler templates are used to build PXE boot files and build the systems using Kickstart and Preseed. 

- Xe commands use Xenserver templates to provision resources on the Xenserver host. Xenserver templates are a copy of those provided by Xen that are customized for: CPU, memory, storage, NIC. Xenserver templates are manually configured.

- DHCP on the Cobbler host provides the initial PXE files, install Yum repo/Apt source

- DNS provision IPs, names through a standalone name server. You must provision DNS manually, there are no hooks currently in this code to update DNS zones for provisioned VMs.
