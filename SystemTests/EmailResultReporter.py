import stresstesting

class EmailResultReporter(stresstesting.ResultReporter):

  _resultString = ""
  _overallPass = True

  def dispatchResults(self, result):
    ''' This relies on the order and names of the items to give the correct output '''
    for t in result.resultLogs():
      if t[0] == 'test_name':
        self._resultString += 'Test ' + t[1] + ' outcome: '
      elif t[0] == 'status':
        self._resultString += t[1] + '\n'
        if t[1] != 'success':
          self._overallPass = False

  def reportStatus(self):
    return self._overallPass

  def sendEmail(self):
    import smtplib
    import socket
    smtpserver = 'outbox.rl.ac.uk'

    errlog = ''
    if self._overallPass:
      RECIPIENTS = ['russell.taylor@stfc.ac.uk','nick.draper@stfc.ac.uk']
      subject = 'Subject: Mantid system tests PASSED\n'
    else:
      RECIPIENTS = 'mantid-developers@mantidproject.org'
      subject = 'To:' + RECIPIENTS + '\r\nSubject: Mantid system tests FAILED\r\n'
      errlog = '\n\nLog files and test result nexus files at: http://download.mantidproject.org/logs/SystemTests\n\n'

    SENDER = 'systemtests@mantidproject.org'
    
    #timeout in seconds
    socket.setdefaulttimeout(180)
    try:
    #Send Email
      session = smtplib.SMTP(smtpserver)
      smtpresult  = session.sendmail(SENDER, RECIPIENTS, subject + self._resultString + errlog)
      session.quit()

      if smtpresult:
          errstr = ""
          for recip in smtpresult.keys():
              errstr = """Could not deliver mail to: %s

    Server said: %s
    %s

    %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
          print errstr
    except smtplib.SMTPException, exc:
      print "Failed to send results email with error:"
      print str(exc)
    except:
      print "Failed to send results email with unknown error"

    return self._overallPass
