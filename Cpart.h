#pragma once

#ifdef CPART_DLL
#define DLL_EXPORT _declspec(dllexport)
#else
#define DLL_EXPORT _declspec(dllexport)
#endif


extern "C"{
	double   getProgress();
    int      mInSec     (char * path);
    int      fileSize   (char * path);
    bool     readf      (char * path, double sInMeas);
    double * transform  (int sectorLength, int pos, bool enableTrend);
    double * amplitude  (int sectorLength, int pos, bool enableTrend);
    double * dispGraph  (int len, int sectorLength, int step, bool enableTrend);
    double * getf       (int start, int len);
    
    void     killDispGraph();
}
