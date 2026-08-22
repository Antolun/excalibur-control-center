# SPDX-License-Identifier: GPL-2.0-or-later
# Makefile for the excalibur-control-center out-of-tree kernel module.

# In-tree Kconfig hook — used when built as part of the kernel tree.
ifneq ($(CONFIG_EXCALIBUR_CONTROL_CENTER),)
obj-$(CONFIG_EXCALIBUR_CONTROL_CENTER) += excalibur.o
else
# Out-of-tree build — CONFIG_ is not set, so force obj-m.
obj-m += excalibur.o
endif

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

package-luppo:
	bash ./build-luppo.sh

.PHONY: all install clean package-luppo
