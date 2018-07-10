CONFIG +=  compile_examples no-libdl qpa largefile precompile_header use_gold_linker sse2 sse3 ssse3 sse4_1 sse4_2 avx avx2 pcre
QT_BUILD_PARTS += libs tools
QT_SKIP_MODULES +=  qtenginio qtlocation qtsensors qtserialport qtserialbus qtquickcontrols2 qtwayland qtcanvas3d qt3d
QT_NO_DEFINES =  ALSA CLOCK_MONOTONIC DBUS EGL EGLFS EGL_X11 EVDEV EVENTFD FONTCONFIG GLIB HARFBUZZ IMAGEFORMAT_JPEG INOTIFY LIBPROXY MREMAP OPENSSL OPENVG POSIX_FALLOCATE PULSEAUDIO STYLE_GTK TSLIB XRENDER ZLIB
QT_QCONFIG_PATH = 
host_build {
    QT_CPU_FEATURES.x86_64 =  cx16 mmx sse sse2 sse3 ssse3
} else {
    QT_CPU_FEATURES.x86_64 =  cx16 mmx sse sse2 sse3 ssse3
}
QT_COORD_TYPE = double
QT_LFLAGS_ODBC   = -lodbc
styles += mac fusion windows
DEFINES += QT_NO_MTDEV
DEFINES += QT_NO_LIBUDEV
DEFINES += QT_NO_EVDEV
DEFINES += QT_NO_TSLIB
DEFINES += QT_NO_LIBINPUT
EXTRA_INCLUDEPATH +=  "/opt/anaconda1anaconda2anaconda3/include"
EXTRA_LIBS +=  -L"/opt/anaconda1anaconda2anaconda3/lib"
sql-drivers = 
sql-plugins =  sqlite
