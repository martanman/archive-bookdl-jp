#!/bin/bash
pages="./_temp_pages"
ordered="./_temp_ordered"

mkdir $pages
mkdir $ordered

python3 autofetch.py $2

cd $ordered
zip $1.zip ./*.jpg
mv $1.zip ..
cd ..

# uncomment to keep a directory containing the non-reordered images
# mkdir $1
# mv ./$pages/*.jpg $1

rm -rf $pages $ordered
