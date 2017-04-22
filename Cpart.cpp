#include "Cpart.h"
#include <netinet/in.h>
#include <fstream>
#include <cmath>
#include <iostream>
#include <complex>

using namespace std;

double d001 = 0;

double * linInterp(double *d1, int l1, int l2)
{
    double *d2 = new double[l2];
    double x;
    for(int i = 0; i < l2-1; i++){
        x = ((double)i)*l1/l2;
        d2[i] = d1[(int)x] + (x - (int)x) * (d1[(int)x+1] - d1[(int)x]);
    }
    d2[l2-1] = d1[l1-1];
    return d2;
}

double * to2deg(double * d, int len)
{
    double curdeg = log2(len);
    if((int)curdeg == ceil(curdeg)) return d;
    return linInterp(d, len, (int)pow(2,ceil(curdeg)));
}

complex<double> * fft(complex<double> * d, int len)
{
	if(len == 1) return d;
    complex<double> * deven = new complex<double>[len/2];
    complex<double> * dodd = new complex<double>[len/2];
    for(int i = 0; i < len/2; i++){
        deven[i] = d[i*2];
        dodd[i] = d[i*2+1];
    }
    deven = fft(deven, len/2);
    dodd = fft(dodd, len/2);
    complex<double> a;
    double mpm2dl = -M_PI*2/len;
    complex<double> * out = new complex<double>[len];
    for(int i = 0; i < len/2; i++){
        a = polar(1.0, mpm2dl*i)*dodd[i];
        out[i] = deven[i]+a;
        out[i+len/2] = deven[i]-a;
    }
    return out;
}

double * trend(double * d, int len){
    int halflen = len/2;
    for (int i = 0; i < len; i++) d[i] = d[i] * abs((i + halflen) % len - halflen) / halflen;
    return d;
}

extern "C" int * test(int len){
    int * a = new int[len];
    for(int i = 0; i < len; i++){
        a[i] = i;
    }
    return a;
}

extern "C" int fileSize(char *c)
{
    ifstream f(c, ios::binary | ios::ate);
    int tellg = f.tellg();
    f.close();
    return tellg;
}

extern "C" int mInSec(char *path){
    int a;
    ifstream fIn(path, ios::binary | ios::in);
    fIn.read((char*)&a, sizeof a);
    fIn.close();
    return ntohl(a);
}

extern "C" int * readf(char * path, double sInQ)
{
    int measInS;
    double measInQ;
    int arrLength = (fileSize(path) - 4) / 2;
    ifstream fIn(path, ios::binary | ios::in);
    fIn.read((char*)&measInS, sizeof measInS);
    measInQ = ntohl(measInS) * sInQ;
    int * out = new int[(int)(arrLength/measInQ)];
    for(int i = 0; i < arrLength/measInQ; i++) out[i] = 0;
    unsigned short us = 0;
    for(int i = 0; i < arrLength; i++){
        fIn.read((char*)&(us), sizeof us);
        us = ntohs(us);
        if(fmod(i, measInQ) < 1 & i > 1) {
            out[(int)(i/measInQ-1)] += int(us * fmod(i, measInQ));
            out[(int)(i/measInQ)] += int(us * (1 - fmod(i, measInQ)));
        } else out[(int)(i/measInQ)] += us;
    }
    fIn.close();
    return out;
}

extern "C" double * transform(double * in, int sectorLength, int pos, bool enableTrend)
{
    double * inCut = new double[sectorLength];
    for(int i = 0; i < sectorLength; i++){
        inCut[i] = in[i+pos];
    }
    if(enableTrend) inCut = trend(inCut, sectorLength);
    int outLength = (int)pow(2, ceil(log2(sectorLength)));
    inCut = to2deg(inCut, sectorLength);
    complex<double> * inCompl = new complex<double>[outLength];
    for(int i = 0; i < outLength; i++) inCompl[i] = inCut[i];
    complex<double> * outCompl = fft(inCompl, outLength);
    double * out  = new double  [outLength];
    for(int i = 0; i < outLength/2; i++){
        out[i*2] = outCompl[i].real();
        out[i*2+1] = outCompl[i].imag();
    }
    for(int i = 0; i < outLength; i++){
        if(abs(out[i]) > 1e20 | out[i] != out[i]){
            out[i] = 0;
        }
    }
    return out;
}

extern "C" double dispersion(double * in, int len)
{
    double sqAv = 0;
    double av = 0;
    for(int i = 0; i < len; i++){
        sqAv += in[i] * in[i];
        av += in[i];
    }
    sqAv /= len;
    av /= len;
    return sqrt(sqAv - av*av);
}

extern "C" double * amplitude(double * in, int sectorLength, int pos, bool enableTrend)
{
    double * outCompl = transform(in, sectorLength, pos, enableTrend);
    sectorLength = (int)pow(2, ceil(log2(sectorLength)));
    double * out  = new double [sectorLength];
    for(int i = 0; i < sectorLength; i++) out[i] = hypot(outCompl[i * 2], outCompl[i * 2 + 1]) / sectorLength * 2;
    return out;
}

extern "C" double * dispGraph(double * in, int len, int sectorLength, int step, bool enableTrend)
{
    int sectorNum = (len - sectorLength) / step;
    int outSectLen = (int)pow(2, ceil(log2(sectorLength)));
    double ** ampl = new double *[sectorNum];
    for(int i = 0; i < sectorNum; i++) ampl[i] = amplitude(in, sectorLength, i * step, enableTrend);
    double * avAmpl = new double[outSectLen];
    for(int i = 0; i < outSectLen; i++){
        avAmpl[i] = 0;
        for(int j = 0; j < sectorNum; j++){
            avAmpl[i] += ampl[j][i];
        }
        avAmpl[i] /= sectorNum;
    }
    double * amplV = new double[sectorNum];
    double * disp = new double[outSectLen];
    for(int i = 0; i < outSectLen; i++){
        for(int j = 0; j < sectorNum; j++) amplV[j] = ampl[j][i];
        disp[i] = dispersion(amplV, sectorNum);
    }
    double * out = new double[outSectLen * 2];
    for(int i = 0; i < outSectLen; i++){
        out[i] = avAmpl[i] == avAmpl[i] ? avAmpl[i] : 0; //if NaN then 0
        out[i + outSectLen] = disp[i] == disp[i] ? disp[i] : 0;
    } 
    return out;
}