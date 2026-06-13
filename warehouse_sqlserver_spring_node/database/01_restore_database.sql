:setvar DatabaseName "S"
:setvar BackupFile "data/S (1).bak"
:setvar DataFile "data/S.mdf"
:setvar LogFile "data/S_log.ldf"

IF DB_ID(N'$(DatabaseName)') IS NOT NULL
BEGIN
  ALTER DATABASE [$(DatabaseName)] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [$(DatabaseName)];
END;
GO

RESTORE DATABASE [$(DatabaseName)]
FROM DISK = N'$(BackupFile)'
WITH
  MOVE N'S' TO N'$(DataFile)',
  MOVE N'S_log' TO N'$(LogFile)',
  REPLACE;
GO
