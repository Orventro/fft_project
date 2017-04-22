#pragma once

#ifdef CPART_DLL
#define DLL_EXPORT _declspec(dllexport)
#else
#define DLL_EXPORT _declspec(dllexport)
#endif

extern "C"{
    int      mInSec    (char * path);
    int      fileSize  (char * path);
    int    * readf     (char * path, double sInMeas);
    double * transform (double * in, int sectorLength, int pos, bool enableTrend);
    double * amplitude (double * in, int sectorLength, int pos, bool enableTrend);
    double * dispGraph (double * in, int len, int sectorLength, int step, bool enableTrend);
    //void     saveActive(char * path);
    //void     saveArray (char * path, double * xArr, double * yArr);
}
