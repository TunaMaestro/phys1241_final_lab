#!/bin/bash
while true
do
	perl -MTime::HiRes -e 'printf("%.3f\n",Time::HiRes::time())'
done

