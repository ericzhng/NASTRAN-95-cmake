# NASTRAN-95

NASTRAN has been released under the  
[NASA Open Source Agreement version 1.3](https://github.com/nasa/NASTRAN-95/raw/master/NASA%20Open%20Source%20Agreement-NASTRAN%2095.doc).


NASTRAN is the NASA Structural Analysis System, a finite element analysis program (FEA) completed in the early 1970's. It was the first of its kind and opened the door to computer-aided engineering. Subsections of a design can be modeled and then larger groupings of these elements can again be modeled. NASTRAN can handle elastic stability analysis, complex eigenvalues for vibration and dynamic stability analysis, dynamic response for transient and steady state loads, and random excitation, and static response to concentrated and distributed loads, thermal expansion, and enforced deformations.

NOTE: There is no technical support available for this software.


## compilation instructions

cmake -G Ninja ..
cmake --build . -j 4
ninja -j 4


set MSYS2_PATH_TYPE=inherit
set MSYSTEM=UCRT64
set CHERE_INVOKING=1
set PATH=C:\msys64\ucrt64\bin;%PATH%

