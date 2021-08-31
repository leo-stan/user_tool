#include <stdio.h>
#define CRC32_POLYNOMIAL 0xEDB88320L
/* --------------------------------------------------------------------------
Calculate a CRC value to be used by CRC calculation functions.
-------------------------------------------------------------------------- */
unsigned long CRC32Value(int i){
	int j;
	unsigned long ulCRC;
	ulCRC = i;
	for ( j = 8 ; j > 0; j-- ){
		if ( ulCRC & 1)
			ulCRC = ( ulCRC >> 1 ) ^ CRC32_POLYNOMIAL;
		else
			ulCRC >>= 1;
		}
	return ulCRC;
}

/* --------------------------------------------------------------------------
Calculates the CRC-32 of a block of data all at once
ulCount - Number of bytes in the data block
ucBuffer - Data block
-------------------------------------------------------------------------- */
unsigned long CalculateBlockCRC32( unsigned long ulCount , unsigned char *ucBuffer ) {
	unsigned long ulTemp1;
	unsigned long ulTemp2;
	unsigned long ulCRC = 0;
	while ( ulCount-- != 0 ){
		ulTemp1 = (ulCRC >> 8 ) & 0x00FFFFFFL;
		ulTemp2 = CRC32Value( ((int) ulCRC ^ *ucBuffer ++ ) & 0xFF);
		ulCRC = ulTemp1 ^ ulTemp2;
	}
return( ulCRC );
}

//main: test from command line
//arg 1 "v" for value or "b" for block
// v -> arg 2 is an integer, return its CRC32Value
//b  -> arg 2 is ulCount, arg 3 is ucBuffer, return the CalculateBlockCRC32

void main(int argc, char **argv){
	//printf("number of arguments = %d\n", argc-1);
	//printf("arguments:\n");
	// for(int i=1; i < argc; i++){
	// 	printf("\t%s\n", argv[i]);
	// }

	//printf("argument 1 is %s\t-> ", argv[1]);

	if(argv[1][0] == 'b'){
		long length = atoi(argv[2]);
		char *block = argv[3];
		printf("block arguments: length = %d, block = %s", length, block);
		
		//use the characters from input as bytes
		long crc = CalculateBlockCRC32(length, block);
		printf("\noutput decimal: %d", crc);

	}
	else if (argv[1][0] == 'v'){
		int i = atoi(argv[2]);
		printf("\nCRC32 Value of %d is %ld", i, CRC32Value(i));
	}
	else{
		printf("\nexpected format:");
		printf("\n\t%s v <i> -> crc32 value of integer", argv[0]);
		printf("\n\t%s b <length> <block> -> crc32 value of block", argv[0]);
	}
	//printf("\nCRC32 Value of %d is %ld", i, CRC32Value(i));
}