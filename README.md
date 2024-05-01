To see both the data from B1 that doesn't match with A1 and the data that matches, you can use two separate columns. In column C, you can list the unmatched data, and in column D, you can list the matched data. Here's how you can do it:

In cell C2, use this formula to list unmatched data:

```excel
=IF(ISERROR(VLOOKUP(B2, A:A, 1, FALSE)), B2, "")
```

In cell D2, use this formula to list matched data:

```excel
=IF(ISNUMBER(VLOOKUP(B2, A:A, 1, FALSE)), B2, "")
```

Then, drag these formulas down for the entire range of your data in column B.

This setup will populate column C with unmatched data from B1 and column D with matched data. Any cell in columns C and D that doesn't have data will be blank.