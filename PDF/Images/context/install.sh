#!/bin/sh

# a user can change the order of the servers to look at
#
# todo: check for a environment variable too so that users can themselves pick a preferred server
# todo: maybe provide instances (not all, say install-lmtx-<data> (we can use an rsnapshot approach)
#
# If your platform is not supported you can set the PLATFORM variable to "native" and compile the
# luametatex engine from github: contextgarden/luametatex. Then move the binary from build/native
# to "installerpath/bin". After the installation you need to populate texroot/texmf-native/bin with
# the binary too. That path should contain:
#
# context.lua    # updated by installer
# mtxrun.lua     # updated by installer
# luametatex     # updated by user
# mtxrun         # symlink to luametatex
# context        # symlink to luametatex

LMTXSERVER=lmtx.pragma-ade.com,lmtx.pragma-ade.nl,lmtx.contextgarden.net
LMTXINSTANCE=install-lmtx
LMTXEXTRAS=

SYSTEM=`uname -s`
CPU=`uname -m`
PLATFORM="unknown"

# maybe also test for: [ -f "$PWD/tex/texmf-native/bin/luametatex" ]

if [ "$1" = "native" ] || [ "$1" = "--native" ] ; then
    PLATFORM="native"
fi

case "$SYSTEM" in
    # linux
    Linux)
        if command -v ldd >/dev/null && ldd --version 2>&1 | grep -E '^musl' >/dev/null
        then
            libc=musl
        else
            libc=glibc
        fi
        case "$CPU" in
            i*86)
                case "$libc" in
                    glibc)
                        PLATFORM="linux" ;;
                    musl)
                        PLATFORM="linuxmusl" ;;
                esac ;;
            x86_64|ia64)
                case "$libc" in
                    glibc)
                        PLATFORM="linux-64" ;;
                    musl)
                        PLATFORM="linuxmusl-64" ;;
                esac ;;
            mips|mips64|mipsel|mips64el)
                PLATFORM="linux-mipsel" ;;
            riscv64)
                PLATFORM="linux-riscv64" ;;
            aarch64)
                PLATFORM="linux-aarch64" ;;
            armv7l)
                PLATFORM="linux-armhf"
                if $(which readelf >/dev/null 2>&1); then
                    readelf -A /proc/self/exe | grep -q '^ \+Tag_ABI_VFP_args'
                    if [ ! $? ]; then
                        PLATFORM="linux-armel"
                    fi
                elif $(which dpkg >/dev/null 2>&1); then
                    if [ "$(dpkg --print-architecture)" = armel ]; then
                        PLATFORM="linux-armel"
                    fi
                fi
                ;;
        esac ;;
            Darwin|darwin)
        case "$CPU" in
            i*86)
                PLATFORM="osx-intel" ;;
            x86_64)
                PLATFORM="osx-64" ;;
            arm64)
                PLATFORM="osx-arm64" ;;
            *)
        esac ;;
            FreeBSD|freebsd)
        case "$CPU" in
            i*86)
                PLATFORM="freebsd" ;;
            amd64)
                PLATFORM="freebsd-amd64" ;;
            *)
        esac ;;
            OpenBSD|openbsd)
        case "$CPU" in
            i*86)
                PLATFORM="openbsd" ;;
            amd64)
                PLATFORM="openbsd-amd64" ;;
            *)
        esac ;;
esac

if test "$PLATFORM" = "unknown" ; then
    echo ""
    echo "Your system \"$SYSTEM $CPU\" is not supported (yet). You can ask"
    echo "on the ConTeXt mailing-list: ntg-context@ntg.nl. If you compile"
    echo "yourself, you can change the PLATFORM variable to native and"
    echo "keep an eye on what happens then."
    exit
fi

# "" are needed for WLS because of (86) in the variable

export PATH="$PWD/bin:$PWD/tex/texmf-$PLATFORM/bin:$PATH"

chmod +x bin/mtxrun

if test "$SYSTEM" = "Darwin" ; then
   if [ `uname -r | cut -f1 -d"."` -gt 18 ]; then
      xattr -d com.apple.quarantine bin/mtxrun
   fi
fi

$PWD/bin/mtxrun --script ./bin/mtx-install.lua --update --server="$LMTXSERVER" --instance="$LMTXINSTANCE" --platform="$PLATFORM" --erase --extras="$LMTXEXTRAS" $@

if test "$PLATFORM" = "native" ; then
    echo "you need to copy luametatex to"
    echo ""
    echo "   $PWD/tex/texmf-$PLATFORM/bin/luametatex"
    echo "   $PWD/bin/mtxrun"
else
    cp $PWD/tex/texmf-$PLATFORM/bin/mtxrun $PWD/bin/mtxrun
fi

cp $PWD/tex/texmf-context/scripts/context/lua/mtxrun.lua      $PWD/bin/mtxrun.lua
cp $PWD/tex/texmf-context/scripts/context/lua/mtx-install.lua $PWD/bin/mtx-install.lua

# echo "  export PATH=$PWD/tex/texmf-$PLATFORM/bin:$PATH"

echo ""
echo "If you want to run ConTeXt everywhere, you need to adapt the path, like:"
echo ""
echo "  export PATH=$PWD/tex/texmf-$PLATFORM/bin:"'$PATH'
echo ""
echo "If you run from an editor you can specify the full path to mtxrun:"
echo ""
echo "  $PWD/tex/texmf-$PLATFORM/bin/mtxrun --autogenerate --script context --autopdf ..."
echo ""
echo "If you also want to run LuaTeX and MkIV you can provide --luatex but first the file"
echo "database has to be generated (this time with context and not mtxrun):"
echo ""
echo "  context --luatex --generate"
echo "  context --luatex --make"
echo ""
echo "The following settings were used:"
echo ""
echo "  server   : $LMTXSERVER"
echo "  instance : $LMTXINSTANCE"
echo "  extras   : $LMTXEXTRAS"
echo "  ownpath  : $PWD"
echo "  platform : $PLATFORM"
echo ""
