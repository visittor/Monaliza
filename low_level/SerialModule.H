/*
*************************** C HEADER FILE ************************************

project   :
filename  : CTEMPLATE.H
version   : 2
date      :

******************************************************************************

Copyright (c) 20xx ,
All rights reserved.

******************************************************************************

VERSION HISTORY:
----------------------------
Version      : 1
Date         :
Revised by   :
Description  :

Version      : 2
Date         :
Revised by   :
Description  : *
               *
               *

******************************************************************************
*/

#ifndef  SerialModule_INCLUDED
#define  SerialModule_INCLUDED

/****************************************************************************/
/**                                                                        **/
/**                              MODULES USED                              **/
/**                                                                        **/
/****************************************************************************/

//#include <stdlib.h>  // depend on application requirements.
//#include "cdat68k.h"  // define data types
#include "CONFIG_PIC24.H"
#include "CDATPIC24.H"
#include "EVENT_DRIVEN_CCS.H"


/****************************************************************************/
/**                                                                        **/
/**                        DEFINITIONS AND MACROS                          **/
/**                                                                        **/
/****************************************************************************/

// RX
#define RX1Q_LN 8
#define RX_FRAME_LENGHT 16
#define START_CHR '<'
#define END_CHR '>'

// TX
#define TX1Q_LN 128


/****************************************************************************/
/**                                                                        **/
/**                        TYPEDEFS AND STRUCTURES                         **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                         EXPORTED VARIABLES                             **/
/**                                                                        **/
/****************************************************************************/

#ifndef SerialModule_C_SRC

#endif

/****************************************************************************/
/**                                                                        **/
/**                       EXPORTED FUNCTIONS                               **/
/**                                                                        **/
/****************************************************************************/
static void VariableOfSerialInit();
static void DynamicMemmoryInit();
static void UARTQueueInit();
static void RecievePackage();
static void SendPackage();
static void MainSerial();
static int8u SendTx1(int8u *strPtr);

/****************************************************************************/
#endif

/****************************************************************************/
/**                                                                        **/
/**                              EOF                                       **/
/**                                                                        **/
/***************************************************************************