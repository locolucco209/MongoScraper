GENCCODE_ASSEMBLY_TYPE=-a gcc-darwin
SO=dylib
SOBJ=dylib
A=a
LIBPREFIX=lib
LIB_EXT_ORDER=.54.1.dylib
COMPILE=gcc-4.2 -DU_ATTRIBUTE_DEPRECATED=   -DU_HAVE_ATOMIC=0  -O3 -arch x86_64 -isysroot /Developer/SDKs/MacOSX10.5.sdk -std=c99 -Wall -pedantic -Wshadow -Wpointer-arith -Wmissing-prototypes -Wwrite-strings   -fno-common -c
LIBFLAGS=-I/opt/anaconda1anaconda2anaconda3/include  -dynamic
GENLIB=gcc-4.2 -dynamiclib -dynamic -O3 -arch x86_64 -isysroot /Developer/SDKs/MacOSX10.5.sdk -std=c99 -Wall -pedantic -Wshadow -Wpointer-arith -Wmissing-prototypes -Wwrite-strings   -arch x86_64 -isysroot /Developer/SDKs/MacOSX10.5.sdk  
LDICUDTFLAGS=
LD_SONAME=-Wl,-compatibility_version -Wl,54 -Wl,-current_version -Wl,54.1 -install_name
RPATH_FLAGS=
BIR_LDFLAGS=
AR=ar
ARFLAGS=r -c
RANLIB=ranlib
INSTALL_CMD=/usr/bin/install -c
