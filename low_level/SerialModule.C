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

#define SerialModule_C_SRC

/****************************************************************************/
/**                                                                        **/
/**                             MODULES USED                               **/
/**                                                                        **/
/****************************************************************************/

#include "SerialModule.H"

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

static volatile Q8UX_STRUCT Tx1QCB;
static volatile int8u Tx1QArray[TX1Q_LN];
static volatile int8u *Tx1BuffPtr;
static volatile int16u Tx1BuffIdx;
static volatile TX1_STATUS Tx1Flag;
static volatile int16u Tx1FrameIn, Tx1FrameOut, Rx1FrameCount,RxCount,Tx1QFullCount, Rx1QFullCount;
static volatile int8u *RxBuffPtr;
static volatile QPTRX_STRUCT Rx1QCB;
static volatile PTR_STRUCT Rx1BuffPtrArray[RX1Q_LN];
static volatile PTR_STRUCT DestPtrStruct;

static volatile int16u MemFail,MemCount;

int8u errCodeMain, SendTx1Count;

/****************************************************************************/
/**                                                                        **/
/**                           EXPORTED FUNCTIONS                           **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                             LOCAL FUNCTIONS                            **/
/**                                                                        **/
/****************************************************************************/
static void VariableOfSerialInit()
{
	Tx1Flag = TX1_READY;
	Tx1BuffIdx = 0;
	Tx1FrameIn = 0;
	Tx1FrameOut = 0;
	Tx1QFullCount = 0;
	Rx1FrameCount = 0;
	RxCount = 0;
	Rx1QFullCount = 0;
	MemFail = 0;
	MemCount = 0;
	return;
}

static void DynamicMemmoryInit()
{
	RxBuffPtr = (int8u *)malloc ((sizeof (int8u)) * RX_FRAME_LENGHT);
	if (RxBuffPtr != (int8u *)NULL)
	{
		MemCount++;
		clear_interrupt(INT_RDA);
		enable_interrupts(INT_RDA);
	}
	else
	{
		MemFail++;
	}
	return;
}

static void UARTQueueInit()
{
	QPtrXInit (&Rx1QCB, Rx1BuffPtrArray, RX1Q_LN);
	Q8UXInit(&Tx1QCB,Tx1QArray,TX1Q_LN);
	return;
}

static int8u SendTx1 (int8u *strPtr)
{
	int8u strLn;
	int8u strIdx;
	int16u qSpace;
	int8u errCode;
	int8u count;
		count = 0;
		strLn = strlen(strPtr);
		if (strLn != 0)
		{
			/* code */
			qSpace = TX1Q_LN - Q8UXCount(&Tx1QCB);
			if (qSpace >= (int16u)strLn)
			{
				/* code */
				for(strIdx = 0; strIdx < strLn; strIdx++)
				{
					Q8UXPut(&Tx1QCB,strPtr[strIdx],&errCode);
					count++;
				}
				if(Tx1Flag == TX1_READY)
				{
					Tx1Flag = TX1_BUSY;
					TX1IF = 1;
					enable_interrupts(INT_TBE);
				}
			}
		}
		return count;
}

static void RecievePackage()
{
	static FRAME_STATE FrameState = FRAME_WAIT;
	static int16u FrmIdx = 0;
	int8u Chr;
	int8u *errCode;
	Chr = getc();
	RxCount++;
	switch(FrameState)
	{
		case FRAME_WAIT:
			if(Chr == START_CHR)
			{
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
				FrameState = FRAME_PROGRESS;
			}
			break;
		case  FRAME_PROGRESS:
			if(Chr == START_CHR)
			{
				FrmIdx = 0;
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
			}
			else if((FrmIdx == (RX_FRAME_LENGHT-2)) && (Chr != END_CHR))
			{
				FrmIdx = 0;
				FrameState = FRAME_WAIT;
			}
			else if (Chr == END_CHR)
			{
				/* code */
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
				RxBuffPtr[FrmIdx] = 0;
				FrmIdx = 0;
				Rx1FrameCount++;

				QPtrXPut(&Rx1QCB,(void *)RxBuffPtr, &errCode);
				if (errCode == Q_FULL)
				{
					/* code */
					free((void *)RxBuffPtr);
					MemCount--;
					Rx1QFullCount++;
				}
				FrameState = FRAME_WAIT;

				RxBuffPtr = (int8u *)malloc((sizeof (int8u)) * RX_FRAME_LENGHT);
				if(RxBuffPtr == (int8u *)NULL)
				{
					disable_interrupts(INT_RDA);
					MemFail++;
				}
				else
				{
					MemCount++;
				}
			}
			else
			{
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
			}
			break;
		default:
			break;
	}
	return;
}

static void SendPackage()
{
	int8u destChr;
	Q_ERR errCode;
	Q8UXGet (&Tx1QCB, &destChr,&errCode);
	if (errCode == Q_OK)
	{
		/* code */
		putc(destChr);
	}
	else
	{
		disable_interrupts(INT_TBE);
		Tx1Flag = TX1_READY;
	}
	return;
}

static void MainSerial()
{
		DisableIntr();
		QPtrXGet(&Rx1QCB,&DestPtrStruct,&errCodeMain);
		if(errCodeMain == Q_OK)
		{
			SendTx1Count = SendTx1((int8u *)DestPtrStruct.blockPtr);
			free ((void *)DestPtrStruct.blockPtr);
			MemCount--;
			EnableIntr();
			if (SendTx1Count == 0)
			{
				/* code */
				output_low(LED3);
			}
		}
		else
		{
			EnableIntr();
		}
}
/****************************************************************************/

/****************************************************************************/
/**                                                                        **/
/**                                 EOF                                    **/
/**                                                                        **/
/****************************************************************************/