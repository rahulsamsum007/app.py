

But ur code is giving me wrong data my arrowdirection contains I and O only and if u didn't fint the matching string in treatment name then return u and dUSE [SRFPalletDB] GO /****** Object: UserDefinedFunction [dbo].[f_getarrow] Script Date: 5/6/2024 12:22:08 PM ******/ SET ANSI_NULLS ON GO SET QUOTED_IDENTIFIER ON GO

ALTER FUNCTION [dbo].[f_getarrow] (@Product varchar(100)) RETURNs VARCHAR(100) AS BEGIN Declare @arrow varchar(1),@prdstr varchar(1),@prdstr1 varchar(1) SELECT @prdstr= substring (@Product, CharIndex ('-', @Product) + 2, 1),@prdstr1=substring (@Product, CharIndex ('-',@Product) + 1, 1)

select @arrow=(Case when @prdstr='I' or @prdstr1='I' then 'U' when @prdstr='O' or @prdstr1='O' then 'D' else '-' end)

RETURN @arrow End

i need wroking poeprly supoose take an exaple if i m giving this SELECT f_getarrow('PX140-IT/OR') FROM DUAL;

i should be getting' IT' and then matching 'IT' with my table ArrowTextMaster i should get "I " from column  treatmentname "IT" and I'll be getting arrowdirection"I " from respective columns is preset in remember I'm using Oracle not swl server five code accordingly 