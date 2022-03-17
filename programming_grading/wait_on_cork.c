/* quick wrapper program to wait on a cork eventfd before executing */
#include <unistd.h>
#include <stdlib.h>

int main(int argc, char** argv) {
    char garbage[8];
    int cork = atoi(argv[1]);
    read(cork, garbage, 8);
    close(cork);
    execv(argv[2], argv+3);
}
