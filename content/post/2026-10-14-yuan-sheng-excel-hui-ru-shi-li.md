---
title: '原生excel汇入示例'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'yuan-sheng-excel-hui-ru-shi-li'
tags: ['bdl', 'excel', 'tiptop']
description: 'sql DEFINE xlapp INTEGER DEFINE xlwb INTEGER MAIN DEFINE result INTEGER DEFINE str STRING --initialization of global variables LET xlapp = -1 LET xlwb = -1 --first, we must create'
draft: false
---

```sql
DEFINE xlapp INTEGER
DEFINE xlwb INTEGER
MAIN
  DEFINE result INTEGER
  DEFINE str STRING
--initialization of global variables
  LET xlapp = -1
  LET xlwb = -1
--first, we must create an Instance of an Excel Application
  CALL ui.Interface.frontCall("WinCOM", "CreateInstance",
   ["Excel.Application"], [xlapp])
  CALL CheckError(xlapp, __LINE__)
--then adding a Workbook to the current document
  CALL ui.interface.frontCall("WinCOM", "CallMethod",
   [xlapp, "WorkBooks.Add"], [xlwb])
  CALL CheckError(xlwb, __LINE__)
--then, setting it to be visible
  CALL ui.interface.frontCall("WinCOM", "SetProperty",
   [xlapp, "Visible", true], [result])
  CALL CheckError(result, __LINE__)
--then CALL SetProperty to set the value of the cell
  CALL ui.Interface.frontCall("WinCOM", "SetProperty", 
   [xlwb, 'activesheet.Range("A1").Value', "foo"],[result])
  CALL CheckError(result, __LINE__)
--then CALL GetProperty to check the value again
  CALL ui.Interface.frontCall("WinCOM", "GetProperty",
   [xlwb, 'activesheet.Range("A1").Value'], [str])
  CALL CheckError(str, __LINE__)
  DISPLAY "content of the cell is: " || str

  --then Free the memory on the client side
  CALL freeMemory()
END MAIN

FUNCTION freeMemory()
 DEFINE res INTEGER
  IF xlwb != -1 THEN
    CALL ui.Interface.frontCall("WinCOM","ReleaseInstance", [xlwb], [res] )
  END IF
  IF xlapp != -1 THEN
    CALL ui.Interface.frontCall("WinCOM","ReleaseInstance", [xlapp], [res] )
  END IF
END FUNCTION
FUNCTION checkError(res, lin)
  DEFINE res INTEGER
  DEFINE lin INTEGER
  DEFINE mess STRING
  IF res = -1 THEN
    DISPLAY "COM Error for call at line:", lin
    CALL ui.Interface.frontCall("WinCOM","GetError",[],[mess])
    DISPLAY mess
--let's release the memory on the GDC side
    CALL freeMemory()
    DISPLAY "Exit with COM Error."
    EXIT PROGRAM (-1)
  END IF
END FUNCTION
```
