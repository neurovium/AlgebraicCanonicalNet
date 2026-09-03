#!/usr/bin/env bash
# Build the SgpDec dependency chain into the user's mamba env at
# /home/nimad/miniforge3/envs/algcanet (GAP 4.15.1 from conda-forge).
set -uo pipefail

P=/home/nimad/miniforge3/envs/algcanet
# sysinfo.gap lives in lib/gap for the conda-forge build; that is the "gaproot"
# package configure scripts want. Packages themselves go in share/gap/pkg,
# which is also on GAPInfo.RootPaths.
GAPROOT=$P/lib/gap
PKG=$P/share/gap/pkg
SRC=$(pwd)/pkgsrc
LOG=$(pwd)/buildlogs
mkdir -p "$LOG"

export CC=$P/bin/x86_64-conda-linux-gnu-gcc
export CXX=$P/bin/x86_64-conda-linux-gnu-g++
export CPPFLAGS="-I$P/include"
export CFLAGS="-O2 -I$P/include"
export CXXFLAGS="-O2 -I$P/include"
export LDFLAGS="-L$P/lib -Wl,-rpath,$P/lib"
export PKG_CONFIG_PATH=$P/lib/pkgconfig
export PATH=$P/bin:$PATH

status=0
for tb in io-4.10.0 orb-5.1.0 datastructures-0.4.3 digraphs-1.15.0 semigroups-5.6.3 genss-1.6.9 sgpdec-1.2.0; do
  echo "=================== $tb ==================="
  d=$PKG/$tb
  if [ ! -d "$d" ]; then
    tar xzf "$SRC/$tb.tar.gz" -C "$PKG" || { echo "UNTAR FAIL $tb"; status=1; continue; }
  fi
  # archive-tag tarballs may unpack under a different dir name
  [ -d "$d" ] || d=$(ls -d "$PKG"/$(echo "$tb" | cut -d- -f1)* | head -1)
  cd "$d" || { status=1; continue; }
  if [ -f ./configure ]; then
    ( ./configure --with-gaproot="$GAPROOT" > "$LOG/$tb.conf.log" 2>&1 \
      && make -j8 > "$LOG/$tb.make.log" 2>&1 ) \
      && echo "BUILT $tb" || { echo "FAIL $tb (see $LOG/$tb.*)"; status=1; }
  else
    echo "PURE-GAP $tb (no configure)"
  fi
done
echo "BUILD_STATUS=$status"
