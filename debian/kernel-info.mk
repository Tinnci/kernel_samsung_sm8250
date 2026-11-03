########################################################################
# Kernel settings
########################################################################

# Kernel variant. This is currently used only on the Source package name.
# Use 'android' for Android kernels ("downstream") or 'mainline' for upstream
# kernels.
VARIANT = android

# Kernel base version
KERNEL_BASE_VERSION = 4.19-325

# The kernel cmdline to use
KERNEL_BOOTIMAGE_CMDLINE = console=tty0 androidboot.hardware=qcom androidboot.memcg=1 video=vfb:640x400,bpp=32,memsize=3072000 msm_rtb.filter=0x237 service_locator.enable=1 swiotlb=2048 firmware_class.path=/vendor/firmware_mnt androidboot.usbcontroller=a600000.dwc3 buildvariant=eng androidboot.selinux=permissive

# Slug for the device vendor. This is going to be used in the KERNELRELASE
# and package names.
DEVICE_VENDOR = samsung

# Slug for the device model. Like above.
DEVICE_MODEL = gts7lwifi

# Slug for the device platform. If unsure, keep this commented.
DEVICE_PLATFORM = kona

# Marketing-friendly full-name. This will be used inside package descriptions
DEVICE_FULL_NAME = Samsung Galaxy Tab S7 Wi-Fi

# Whether to use configuration fragments to augment the kernel configuration.
# If unsure, keep this to 0.
KERNEL_CONFIG_USE_FRAGMENTS = 1

# Whether to use diffconfig to generate the device-specific configuration.
# If you enable this, you should set KERNEL_CONFIG_USE_FRAGMENTS to 1.
# If unsure, keep this to 0.
KERNEL_CONFIG_USE_DIFFCONFIG = 0

KERNEL_CONFIG_EXTRA_FRAGMENTS = kona-sec-common.config gts7lwifi.config extra.config

# Defconfig to use
KERNEL_DEFCONFIG = vendor/kona-perf_defconfig

# Whether to include DTBs with the image. Use 0 (no) or 1.
KERNEL_IMAGE_WITH_DTB = 1

# Path to the DTB
# If you leave this undefined, an attempt to find it automatically
# will be made.
KERNEL_IMAGE_DTB = arch/arm64/boot/dts/vendor/qcom/*.dtb

# Whether to include a DTB Overlay. Use 0 (no) or 1.
KERNEL_IMAGE_WITH_DTB_OVERLAY = 1

# Path to the DTB overlay.
# T870 ships EU HW revs r02..r07 as separate dtbo overlays (no r00/r01 for wifi-only).
KERNEL_IMAGE_DTB_OVERLAY = arch/arm64/boot/dts/samsung/gts7l/*.dtbo

# Whether to include the DTB Overlay into the kernel image
# Use 0 (no, default) or 1.
# dtbo.img will always be shipped in the linux-bootimage- package.
KERNEL_IMAGE_WITH_DTB_OVERLAY_IN_KERNEL = 0

# Various other settings that will be passed straight to mkbootimg
KERNEL_BOOTIMAGE_PAGE_SIZE = 4096
KERNEL_BOOTIMAGE_BASE_OFFSET = 0x00000000
KERNEL_BOOTIMAGE_KERNEL_OFFSET = 0x00008000
KERNEL_BOOTIMAGE_INITRAMFS_OFFSET = 0x01000000
KERNEL_BOOTIMAGE_SECONDIMAGE_OFFSET = 0x00f00000
KERNEL_BOOTIMAGE_TAGS_OFFSET = 0x00000100
KERNEL_BOOTIMAGE_DTB_OFFSET = 0x01f00000

# Kernel bootimage version. Defaults to 0 (legacy header).
# Devices launched with Android 10: version 2
KERNEL_BOOTIMAGE_VERSION = 2

########################################################################
# Android verified boot
########################################################################

# Whether to build a flashable vbmeta.img. Please note that currently
# only empty vbmeta images (disabling verified boot) can be generated.
# Use 0 (no) or 1 (default).
DEVICE_VBMETA_REQUIRED = 1

# Samsung devices require a special flag. Enable the following if your
# device is a Samsung device that requires flag 0 to be present
# Use 0 (no, default) or 1.
DEVICE_VBMETA_IS_SAMSUNG = 1

########################################################################
# Automatic flashing on package upgrades
########################################################################

# Whether to enable kernel upgrades on package upgrades. Use 0 (no) or 1.
FLASH_ENABLED = 1

# Tab S7 is A-only (single boot partition, no slot_suffix).
FLASH_IS_AONLY = 1

# Do not enable if you don't know what you're doing
FLASH_IS_LEGACY_DEVICE = 0

# Device manufacturer. Must match ro.product.vendor.manufacturer.
FLASH_INFO_MANUFACTURER = samsung

# Device model. Must match ro.product.vendor.model.
FLASH_INFO_MODEL = SM-T870

# Device CPU. Last-resort match against /proc/cpuinfo.
FLASH_INFO_CPU = Qualcomm Technologies, Inc KONA

# Supported device ids.
FLASH_INFO_DEVICE_IDS = SM-T870 gts7lwifi

########################################################################
# Kernel build settings
########################################################################

# Whether to cross-build. Use 0 (no) or 1.
BUILD_CROSS = 1

# (Cross-build only) The build triplet to use.
BUILD_TRIPLET = aarch64-linux-android-

# (Cross-build only) The build triplet to use with clang.
BUILD_CLANG_TRIPLET = aarch64-linux-gnu-

# The compiler to use. Recent Android kernels are built with clang.
BUILD_CC = clang
CLANG_CUSTOM = 1

# Extra paths to prepend to the PATH variable.
BUILD_PATH = /usr/lib/llvm-android-14.0-r450784d/bin

# Suppress Samsung-downstream strict -Werror on unused variables.
KERNEL_BUILD_FLAGS = KCFLAGS="-Wno-error=unused-variable -Wno-error=unused-but-set-variable -Wno-error=unused-function -Wno-error=unused-const-variable"

# Extra packages to add to the Build-Depends section.
DEB_TOOLCHAIN = device-tree-compiler, linux-initramfs-halium-generic:arm64, binutils-aarch64-linux-gnu, clang-android-14.0-r450784d, gcc-4.9-aarch64-linux-android, g++-4.9-aarch64-linux-android, libgcc-4.9-dev-aarch64-linux-android-cross

# Where we're building on
DEB_BUILD_ON = amd64

# Where we're going to run this kernel on
DEB_BUILD_FOR = arm64

# Target kernel architecture
KERNEL_ARCH = arm64

# Kernel target to build.
KERNEL_BUILD_TARGET = Image
