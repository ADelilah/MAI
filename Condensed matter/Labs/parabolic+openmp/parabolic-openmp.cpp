#include <math.h>
#include <iostream>
#include <fstream>
#include <omp.h>
#define pi M_PI

using namespace std;

#define A  1
#define min_x 0
#define max_x 1
#define min_t 0
#define max_t 1
#define step_x 0.1
#define step_t 0.001

int n_x = 1 + (max_x - min_x) / step_x;
int n_t = 1 + (max_t - min_t) / step_t;

double k = double(A * step_t) / double(step_x * step_x);
double k2 = 1 - 2 * k;

double **u;

double init_f(double x) {
    return x + sin(pi * x);
}

void print(int l) {
    for (int j = 0; j < n_x; ++j) {
        cout << u[l][j] << ' ';
    }
    cout << endl;
}

int main() {
    if (k > 0.5) {
        cout << "The scheme is not stable! sigma = " << k << " > 0.5" << endl;
        return 0;
    }

    u = new double*[n_t];

    for (int i = 0; i < n_t; ++i) {
        u[i] = new double[n_x];
        #pragma omp parallel for num_threads(4)
        for (int j = 0; j < n_x; ++j) {
            if (i) {
                u[i][j] = 0;
            } else {
                double x = min_x + j * step_x;
                u[i][j] = init_f(x);
            }
        }
    }

    for (int t = 1; t < n_t; ++t) {
        #pragma omp parallel for num_threads(4)
        for (int i = 1; i < n_x-1; ++i) {
            u[t][i] = u[t-1][i+1] * k + u[t-1][i] * k2 + u[t-1][i-1] * k;
        }
        u[t][0] = 0;
        u[t][n_x-1] = 1;
    }

    std::fstream fs;
    fs.open ("output.txt", std::fstream::out);
    for (int i = 0; i < n_t; ++i) {
        for (int j = 0; j < n_x; ++j) {
            fs << u[i][j] << ' ';
        }
        fs << endl;
    }

}
