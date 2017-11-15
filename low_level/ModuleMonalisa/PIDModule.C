/*
*************************** C SOURCE FILE ************************************

project   :
filename  : CTEMPLATE.C
version   : 2
date      :

******************************************************************************

Copyright (c) 20xx
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

#define PIDModule_C_SRC

/****************************************************************************/
/**                                                                        **/
/**                             MODULES USED                               **/
/**                                                                        **/
/****************************************************************************/

#include "PIDModule.h"

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


/****************************************************************************/
/**                                                                        **/
/**                      PROTOTYPES OF LOCAL FUNCTIONS                     **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                           EXPORTED VARIABLES                           **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                            GLOBAL VARIABLES                            **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                           EXPORTED FUNCTIONS                           **/
/**                                                                        **/
/****************************************************************************/
void InitialPID(PIDParameter *MOTOR,float Kp,float Ki,float Kd)
{
	
	MOTOR->Kp = Kp;
	MOTOR->Ki = Ki;
	MOTOR->Kd = Kd;

	MOTOR->error = 0;

	MOTOR->previousError = 0;
	MOTOR->errorSummation = 0;
	MOTOR->u = 0;

	// Paremeter for velocity form
	
	MOTOR->delta_u = 0;
	MOTOR->PreviousU1 = 0;
	MOTOR->PreviousE1 = 0;
	MOTOR->PreviousE2 = 0;
}


void PIDPositionalForm(PIDParameter *MOTOR)
{
	MOTOR->errorSummation += MOTOR->error;
	MOTOR->previousError = MOTOR->error;

	MOTOR->u = (MOTOR->Kp * MOTOR->error) + (MOTOR->Ki * MOTOR->errorSummation) + (MOTOR->Kd*(MOTOR->error - MOTOR->previousError));
}

void PIDVelocityForm(PIDParameter *MOTOR)
{

	MOTOR->delta_u = ((MOTOR->Kp + MOTOR->Ki + MOTOR->Kd)*MOTOR->error)-((MOTOR->Kp+2*MOTOR->Kd)*MOTOR->PreviousE1) + MOTOR->Kd*MOTOR->PreviousE2;
	MOTOR->u = MOTOR->PreviousU1 + MOTOR->delta_u;
	// if(MOTOR->u > 750)
	// {
	// 	MOTOR->u = 750;
	// }
	MOTOR->PreviousU1 = MOTOR->u;
	MOTOR->PreviousE2 = MOTOR->PreviousE1;
	MOTOR->PreviousE1 = MOTOR->error;

}

/****************************************************************************

Motor Control Zone

*****************************************************************************/

void InitialMotorControl(MotorParameter *MOTORXY)
{
	MOTORXY->countDistance = 0;
	MOTORXY->currentDistance = 0;
	MOTORXY->directionRead = 0;

	MOTORXY->TimeOld = 0;
	MOTORXY->TimeNew = 0;
	MOTORXY->interval = 0;

	MOTORXY->StateCH = 0;

	MOTORXY->referenceDesire = 0;
}

void InitialInterruptController()
{
	set_compare_time(1,0);
	setup_compare(1,COMPARE_PWM | COMPARE_TIMER3);

	set_compare_time(2,0);
	setup_compare(2,COMPARE_PWM | COMPARE_TIMER3);

	set_timer3(0);
	setup_timer3(TMR_INTERNAL | TMR_DIV_BY_1 , 999);
	/* FreqPWM = 16 MHz  / 10000 = 1.6 KHz | Now 16 KHz*/ 

	setup_capture(1, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC1);
	enable_interrupts(INT_IC1);

	setup_capture(2, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC2);
	enable_interrupts(INT_IC2);

	setup_capture(3, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC3);
	enable_interrupts(INT_IC3);

	setup_capture(4, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC4);
	enable_interrupts(INT_IC4);
	/* INPUT CAPTURE PULSE OF ENCODER */
	/* Try to read encoder and on/off led represent CHA CHB */

	set_timer2(0);
	setup_timer2(TMR_INTERNAL | TMR_DIV_BY_1 , 65535);
	

	clear_interrupt(INT_TIMER5);
	set_timer5(0);
	setup_timer5(TMR_INTERNAL | TMR_DIV_BY_256,6249);
	enable_interrupts(INT_TIMER5);
}


void MovingMotor(AXIS xyaxis,int16u speed,int8u direction)
{
	if(xyaxis == XAXIS)
	{
		MovingMotorX(speed,direction);
	}

	else if(xyaxis == YAXIS)
	{
		MotorMovingY(speed,direction);
	}
}

/*
Sub function of MovingMotor XAXIS ans YAXIS
*/

void MovingMotorX(int16u speed,int8u direction)
{
	if(speed >= 750)
	{
		speed = 750;
	}

	if (direction == CCW)
	{
		set_pwm_duty(1,speed);
		output_high(MOTORINX1);
		output_low(MOTORINX2);
	}
	else if (direction == CW)
	{
		set_pwm_duty(1,speed);
		output_high(MOTORINX2);
		output_low(MOTORINX1);
	}
	else if (direction == BREAK)
	{
		set_pwm_duty(1,0);
		output_low(MOTORINX1);
		output_low(MOTORINX2);
	}
}

void MotorMovingY(int16u speed , int8u direction)
{
	if(speed >= 750)
	{
		speed = 750;
	}

	if (direction == CW)
	{
		set_pwm_duty(2,speed);
		output_high(MOTORINY1);
		output_low(MOTORINY2);
	}
	else if (direction == CCW)
	{
		set_pwm_duty(2,speed);
		output_high(MOTORINY2);
		output_low(MOTORINY1);
	}
	else if (direction == BREAK)
	{
		set_pwm_duty(2,0);
		output_low(MOTORINY1);
		output_low(MOTORINY2);
	}

}

/*****************************************************************************

Read Position

*****************************************************************************/

void qudratureEncoderChannelAXAxis(MotorParameter *MOTORXY)
{
	int16u ip = (input_b () & 0x0030);

	MOTORXY->TimeNew = get_capture (1);
	MOTORXY->interval = MOTORXY->TimeNew - MOTORXY->TimeOld;
	MOTORXY->StateCH = ~(((ip & 0x10)>>4) ^ ((ip & 0x20)>>5)) & 0x01;
	if ( (ip & 0x10)>>4 == (ip & 0x20)>>5 ) {
		MOTORXY->directionRead = 1;
		MOTORXY->countDistance += 1;
	}
	else{
		MOTORXY->directionRead = 2;
		MOTORXY->countDistance -= 1;
	}
	MOTORXY->TimeOld = MOTORXY->TimeNew;
}

void qudratureEncoderChannelBXAxis(MotorParameter *MOTORXY)
{
	int16u ip = (input_b () & 0x0030);

	MOTORXY->TimeNew = get_capture (2);
	MOTORXY->interval = MOTORXY->TimeNew - MOTORXY->TimeOld;
	MOTORXY->StateCH = ~(((ip & 0x10)>>4) ^ ((ip & 0x20)>>5)) & 0x01;
	if ( (ip & 0x10)>>4 != (ip & 0x20)>>5 ) {
		MOTORXY->directionRead = 1;
		MOTORXY->countDistance += 1;
	}
	else{
		MOTORXY->directionRead = 2;
		MOTORXY->countDistance -= 1;
	}
	MOTORXY->TimeOld = MOTORXY->TimeNew;
}

void qudratureEncoderChannelAYAxis(MotorParameter *MOTORXY)
{
	int16u ip = (input_b () & 0x00c0);

	MOTORXY->TimeNew = get_capture (3);
	MOTORXY->interval = MOTORXY->TimeNew - MOTORXY->TimeOld;
	MOTORXY->StateCH = ~(((ip & 0x40)>>6) ^ ((ip & 0x80)>>7)) & 0x01;
	if ( (ip & 0x40)>>6 == (ip & 0x80)>>7 ) {
		MOTORXY->directionRead = 1;
		MOTORXY->countDistance -= 1;
	}
	else{
		MOTORXY->directionRead = 2;
		MOTORXY->countDistance += 1;
	}
	MOTORXY->TimeOld = MOTORXY->TimeNew;
}

void qudratureEncoderChannelBYAxis(MotorParameter *MOTORXY)
{
	int16u ip = (input_b () & 0x00c0);

	MOTORXY->TimeNew = get_capture (4);
	MOTORXY->interval = MOTORXY->TimeNew - MOTORXY->TimeOld;
	MOTORXY->StateCH = ~(((ip & 0x40)>>6) ^ ((ip & 0x80)>>7)) & 0x01;
	if ( (ip & 0x40)>>6 != (ip & 0x80)>>7 ) {
		MOTORXY->directionRead = 1;
		MOTORXY->countDistance -= 1;
	}
	else{
		MOTORXY->directionRead = 2;
		MOTORXY->countDistance += 1;
	}
	MOTORXY->TimeOld = MOTORXY->TimeNew;
}

void computeDistance(MotorParameter *MOTORXY)
{
	MOTORXY->currentDistance = (((MOTORXY->countDistance*(7.5/64))*3.14)/180)*RadiusOfPulley;
}
/****************************************************************************/
/**                                                                        **/
/**                             LOCAL FUNCTIONS                            **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/

/****************************************************************************/
/**                                                                        **/
/**                                 EOF                                    **/
/**                                                                        **/
/****************************************************************************/