#!/bin/bash

#
# Copyright 2024 Marc Mosko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

TARS=(
  binutils/binutils-2.43.tar.gz
  binutils/binutils-2.43.1.tar.gz
  binutils/binutils-2.44.tar.gz
	bison/bison-3.7.tar.gz
	bison/bison-3.7.1.tar.gz
	bison/bison-3.7.2.tar.gz
	bison/bison-3.7.3.tar.gz
	bison/bison-3.7.4.tar.gz
	bison/bison-3.7.5.tar.gz
	bison/bison-3.7.6.tar.gz
	bison/bison-3.8.tar.gz
	bison/bison-3.8.1.tar.gz
	bison/bison-3.8.2.tar.gz
	emacs/emacs-29.tar.gz
	emacs/emacs-29.1.tar.gz
	emacs/emacs-29.2.tar.gz
	emacs/emacs-29.3.tar.gz
	emacs/emacs-29.4.tar.gz
	gcc/gcc-12.1.0/gcc-12.1.0.tar.gz
	gcc/gcc-12.2.0/gcc-12.2.0.tar.gz
	gcc/gcc-12.3.0/gcc-12.3.0.tar.gz
	gcc/gcc-12.4.0/gcc-12.4.0.tar.gz
	patch/patch-2.7.tar.gz
	patch/patch-2.7.1.tar.gz
	patch/patch-2.7.2.tar.gz
	patch/patch-2.7.3.tar.gz
	patch/patch-2.7.4.tar.gz
	patch/patch-2.7.5.tar.gz
	patch/patch-2.7.6.tar.gz
	)

mkdir -p tar
for f in "${TARS[@]}"; do
	base=$(basename -- $f)
	echo "$f => $base"
	wget --no-check-certificate https://ftp.gnu.org/gnu/$f -O tar/$base
	done
