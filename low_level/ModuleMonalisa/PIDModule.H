
/*************************** C HEADER FILE ************************************

project   :
filename  : PIDModule.H
version   : 2
date      :

******************************************************************************

Copyright (c) 2017 ,
All rights reserved.

******************************************************************************

VERSION HISTORY:
----------------------------
Version      : 2
Date         : 13/11/2017
Revised by   : Nasrun Hayeeyama
Description  : Calculate exact input by PID controller. Version 2 We will put MotorDrive Function .

Version      : 2
Date         :
Revised by   :
Description  : *
               *
               *

******************************************************************************
*/

#ifndef PIDModule_INCLUDED
#define PIDModule_INCLUDED

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

#define MOTORINX1 PIN_A2
#define MOTORINX2 PIN_A4
#define ENABLEAX1 PIN_B2

#define MOTORINY1 PIN_A0
#define MOTORINY2 PIN_A1
#define ENABLEAY1 PIN_B0

#define CCW 0
#define CW 1
#define BREAK 2

#define RadiusOfPulley 7

/****************************************************************************/
/**                                                                        **/
/**                        TYPEDEFS AND STRUCTURES                         **/
/**                                                                        **/
/****************************************************************************/
typedef struct{
	float Kp;
	float Ki;
	float Kd;

	float error;

	float previousError;
	float errorSummation;
	float u;

	// Paremeter for velocity form
	
	float delta_u;
	float PreviousU1;
	float PreviousE1;
	float PreviousE2;

}PIDParameter;

typedef struct 
{
	/*	Read Variable */
	float referenceDesire;
	
	int16u countDistance;
	float currentDistance;
	int8u directionRead;

	/*	Time-space Variable */
	int16u TimeNew;
	int16u TimeOld;
	int16u interval;

	int8u StateCH;
	
	
}MotorParameter;

typedef volatile enum
{
	XAXIS,
	YAXIS
}AXIS;


/****************************************************************************/
/**                                                                        **/
/**                         EXPORTED VARIABLES                             **/
/**                                                                        **/
/****************************************************************************/

#ifndef PIDModule_C_SRC

#endif

/****************************************************************************/
/**                                                                        **/
/**                       EXPORTED FUNCTIONS                               **/
/**                                                                        **/
/****************************************************************************/

/****************************************************************************

Position control zone

*****************************************************************************/
void InitialPID(PIDParameter *MOTOR, float Kp,float Ki,float Kd);
/*******************************************
PID Positional Form 
Parameter : e
Return : u
Compute control input from error in positional form
*******************************************/
void PIDPositionalForm(PIDParameter *MOTOR);

/*******************************************
PID Velocity Form 
Parameter : e
Return : u
Compute control input from error in velocity form
*******************************************/
void PIDVelocityForm(PIDParameter *MOTOR);

/****************************************************************************

Motor Control Zone

*****************************************************************************/

void InitialMotorControl(MotorParameter *MOTORXY);
void InitialInterruptController();


void MovingMotor(AXIS xyaxis,int16u speed,int8u direction);

/*
Sub function of MovingMotor XAXIS ans YAXIS
*/

void MovingMotorX(int16u speed , int8u direction);
void MotorMovingY(int16u speed , int8u direction);

/*****************************************************************************

Read Position

*****************************************************************************/

void qudratureEncoderChannelAXAxis(MotorParameter *MOTORXY);
void qudratureEncoderChannelBXAxis(MotorParameter *MOTORXY);

void qudratureEncoderChannelAYAxis(MotorParameter *MOTORXY);
void qudratureEncoderChannelBYAxis(MotorParameter *MOTORXY);

void computeDistance(MotorParameter *MOTORXY);


/****************************************************************************/
#endif

/****************************************************************************/
/**                                                                        **/
/**                              EOF                                       **/
/**                                                                        **/
/***************************************************************************/