Gabriel Modifications
=====================

* 2012-12 boursorama banque: there is a blocking two factor authentification sometimes, when boursorama backend does not recognize the computer. For security reasons, they prevent access to accounts unless the legitimate user enters a PIN code that he receives in its cellphone. There is no way to bypass this limitation.
I've added a page to boursorama backend as well as configuration to detect this new state, and trigger the sms delivery. The user has to enter it in the console, and can then access its normal accounts.
Pay attention there is a daily limitation in SMS delivery (around 15).
