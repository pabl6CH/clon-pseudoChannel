# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 22:59:57 2018

@author: Matt
"""

from pseudo_config import plexLibraries as local_commercials

commercials = local_commercials["Commercials"]
movies = local_commercials["Movies"]
tvs = local_commercials["TV Shows"]

commercials_file = open('Commercial_Libraries.txt','w')
movies_file = open('Movie_Libraries.txt','w')
tvs_file = open('TV_Libraries.txt','w')
for commercial in commercials:
    commercials_file.write(commercial + '\n')
for movie in movies:
    movies_file.write(movie + '\n')
for tv in tvs:
    tvs_file.write(tv + '\n')
    
commercials_file.close()
movies_file.close()
tvs_file.close()



