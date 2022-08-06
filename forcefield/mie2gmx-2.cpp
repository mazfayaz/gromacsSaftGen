// Tabulated Mie Potential For GROMACS 
// Date and comments:
// Aug 03 2012 at Imperial College London, Hello World, C.Herdes
// Oct 09 2012 at Imperial College London, restriction max energy
 
#include <iostream>
#include <stdio.h> 
#include <math.h> 
#include <sstream>
#include <string>
using namespace std;

int main() 
{ 
    FILE           *fout; 
    double             r;
	double        cutoff;
	double             n;
	double             m;
	stringstream  myFile;
	cout << "This program generates a tabulated Mie potential for GROMACS,\nplease read http://www.sklogwiki.org/SklogWiki/index.php/Mie_potential for notation.\n#\nPlease, enter a value for n = ";
	cin >> n;
	cout << "Please, enter a value for m = ";
	cin >> m;
	cout << "Please, enter a value for the cut-off = ";
	cin >> cutoff;
	myFile << "tableMIE_"<< n << "_" << m << ".xvg";
	string myTable(myFile.str());
	const char* cstr1 =myTable.c_str();
	fout = fopen(cstr1, "w");
	double c_mie = n/(n-m)*pow(n/m,m/(n-m));	 
    fprintf(fout, "# CHerdes Imperial College London 2012\n# Tabulated Mie Potential n:%f and m:%f\n# Please calculate your A = %f x Epsilon x Sigma^%f and C = %f x Epsilon x Sigma^%f.\n", n, m, c_mie, n, c_mie, m); 
    for (r=0; r<=cutoff+1; r+=0.002) { 
        double f = 1/r; 
        double fprime = 1/(pow(r,2)); 
        double g = -1/(pow(r,m)); 
        double gprime = -m/(pow(r,m+1)); 
        double h = 1/(pow(r,n)); 
        double hprime = n/(pow(r,n+1)); 
        /* print output */ 
        if (hprime>1e35) { 
            fprintf(fout, "%12.10e   %12.10e %12.10e   %12.10e %12.10e   %12.10e %12.10e\n", r,0.0,0.0,0.0,0.0,0.0,0.0); 
        } else { 
            fprintf(fout, "%12.10e   %12.10e %12.10e   %12.10e %12.10e   %12.10e %12.10e\n", r,f,fprime,g,gprime,h,hprime); 
        } 
    } 
    fclose(fout);
	cout << myFile.str() << " now can be found in the current directory, enjoy!\n";
    return(0); 
}
