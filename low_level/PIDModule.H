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

#ifndef  PIDModule_INCLUDED
#define  PIDModule_INCLUDED

/****************************************************************************/
/**                                                                        **/
/**                              MODULES USED                              **/
/**                                                                        **/
/****************************************************************************/

//#include <stdlib.h>  // depend on application requirements.
//#include "cdat68k.h"  // define data types
#include "CONFIG_PIC24.H"
#include "CDATPIC24.H"

/****************************************************************************/
/**                                                                        **/
/**                        DEFINITIONS AND MACROS                          **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                        TYPEDEFS AND STRUCTURES                         **/
/**                                                                        **/
/****************************************************************************/

typedef struct{
	float Kp;
	float Ki;
	float Kd;

	float previousError;
	float errorSummation;
	float u;

	// Paremeter for velocity form
	
	float delta_u;
	float PreviousU1;
	float PreviousE1;
	float PreviousE2;

}PIDParameter;

/****************************************************************************/
/**                                                                        **/
/**                         EXPORTED VARIABLES                             **/
/**                                                                        **/
/****************************************************************************/

void InitialPID(PIDParameter *MOTOR);
/*******************************************
PID Positional Form 
Parameter : e
Return : u
Compute control input from error in positional form
*******************************************/
void PIDPositionalForm(float error, PIDParameter *MOTOR);

/*******************************************
PID Velocity Form 
Parameter : e
Return : u
Compute control input from error in velocity form
*******************************************/
void PIDVelocityForm(float error, PIDParameter *MOTOR);


#ifndef PIDModule_C_SRC

#endif

/****************************************************************************/
/**                                                                        **/
/**                       EXPORTED FUNCTIONS                               **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
#endif

/****************************************************************************/
/**                                                                        **/
/**                              EOF                                       **/
/**                                                                        **/
/****************************************************************************/