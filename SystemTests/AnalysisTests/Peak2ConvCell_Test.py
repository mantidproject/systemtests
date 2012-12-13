import stresstesting
import numpy
from numpy import matrix
from numpy import linalg
import math
import random
import mantid
from mantid.simpleapi import *
#from mantidsimple import *
#TODO premultiply cases, fix up.. Maybe not needed Cause Conv cell was "Nigglied"
#TODO: SWitch cases, if use approx inequality, may get error cause low level code  [does Not](does) premult but when it [should](should not)
class Peak2ConvCell_Test(stresstesting.MantidStressTest):
   conventionalUB=numpy.zeros(shape=(3,3))
   Cubic=[1,3,5]
   Tetr=[6,7,11,15,18,21]
   Orth=[8,13,16,19,23,26,32,36,38,40,42]
   Hex = [2,4,9,12,22,24]
   Tricl=[31,44]
   Mon=[28,29,30,33,34,35,43]
   MonI=[17,27]
   MonC=[10,14,20,25,37,39,41]
   CentP=[11,12,21,22,31,32,33,34,35,44]
   CentF=[1,3,9,16,26]
   CentI=[2,4,5,6,7,8,10,14,15,17,18,19,20,24,25,27,37,39,41,42,43]
   CentC=[10,13,14,17,20,23,25,27,28,29,30,36,37,38,39,40,41]
   
  
   def CalcConventionalUB(self,a,b,c,alpha,beta,gamma,type):
      Res= matrix([[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])
      
      if type=='O':
        
        Res[0,0]=1./a
        Res[1,1]=1./b
        Res[2,2]=1./c
       
      elif type=='H':
         Res[0,0]= a*1.0
         Res[1,0]= -a/2.
         Res[1,1]= a*.866
         Res[2,2]=c*1.0
         Res=Res.I
      else:
         if alpha <=90:
            self.conventionalUB = None
            return None
         Res[0,0] = a*1.0
         Res[1,1] = b*1.0
         Alpha = (alpha*math.pi/180)
         Res[2,0] = c*math.cos( Alpha)
         Res[2,2] = c*math.sin(Alpha)
         # Now Nigglify the matrix( get 3 smallest sides)
         #print "Orig"
         #print Res
         n =0
         YY=0
         if( a <=c):
            n = (int)(-Res[2,0]/a)
            YY= Res[2,0] +n*a
          
         else:
        
           n= (int)(-a*Res[2,0]/(c*c)-.5)
           YY=n*Res[2,0]+a
        
         #print ["A",YY,n]
         sgn=1
         if( a <= c):
            
            if ( math.fabs( YY + a ) < math.fabs( YY ) and a <= c ):
              
               YY += a
               sgn = -1
               n=n+1 
            
         
         elif( (YY+Res[2,0])*(YY+Res[2,0])+(n+1)*(n+1)*Res[2,2]*Res[2,2] < a*a):
          
            YY+=Res[2,0]
            n=n+1
            sgn = -1
           
         #print ["B",YY,sgn,n]
        
         if( n>0 ):
            if( a <= c):
          
               Res[2,0]= sgn*YY
               Res[2,2] *=sgn
             
            else:
          
               if( YY*Res[2,0]+n*Res[2,2]*Res[2,2] > 0):
                   sgn =-1
                   
               else:
                   sgn = 1
               Res[0,0]= sgn*YY
               Res[0,2] =sgn*n*Res[2,2]
               
          
         #print Res
         Res=Res.I 
         
      
      self.conventionalUB = Res
   
      return Res
  
       
   def Niggli( self, Res):
      RUB= Res.I
      X=RUB*RUB.T
      done = False
      while not done:
         done = True
         for i in range(2):
            if X[i,i]>X[i+1,i+1]:
               done = False
               for j in range(3):
                  sav= RUB[i,j]
                  RUB[i,j]=RUB[i+1,j]
                  RUB[i+1,j]=sav
                  X=RUB*RUB.T
         if not done:
            continue
         for i in range(2):
            if X[i,i]<2*math.fabs(X[i,2]):
               sgn=1
               if X[i,2] >0:
                  sgn=-1
               for j in range(3):
                  RUB[2,j]=RUB[2,j]+sgn*RUB[i,j]
               done=False
               X=RUB*RUB.T
               break
               
      if( numpy.linalg.det( RUB )< 0):
        for  cc in range(3):
           RUB[0,cc] *=-1  
           
      return RUB.I  
          
   def CalcNiggliUB( self,a, b,c,alpha, beta, gamma,type, Center):
    
      if( Center=='P'):
         X = self.CalcConventionalUB( a,b,c,alpha,beta,gamma,type)          
         return X      
     
      Res= matrix([[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])
      ConvUB = self.CalcConventionalUB(a,b,c,alpha,beta,gamma,type)
      if( ConvUB== None):
         return None
      
      ResP =  numpy.matrix.copy(ConvUB)
      ResP =ResP.I
  
      if( type=='H' and Center =='I'):
         Center ='R'
      
      if( Center == 'I'):
      
         s1=1
         s2=1
         for  r in range(0,3):
            for cc in range(3):
           
               
               if( cc==0):
                  if( r>0):
                  
                     s1 = (-1)**r
                     s2 =-s1
                  
               Res[r,cc] =ResP[0,cc]/2+s1*ResP[1,cc]/2+s2*ResP[2,cc]/2
            
         Res=Res.I
      
      elif( Center =='F'):
      
         if( type =='H'  or  type=='M'):
            return None
         
         ss = [0,0,0]
        
         for  r in range(3):
            for cc in range(3):
            
               ss=[1,1,1]
               ss[r]=0
               
               Res[r,cc]=ss[0]*ResP[0,cc]/2+ss[1]*ResP[1,cc]/2+ss[2]*ResP[2,cc]/2
       
         Res=Res.I
      
      elif( Center =='A' or Center=='B'or Center=='C'):
      
         if( type =='H' ):
            return None
         if( type =='M'  and  Center== 'B'):
            return None
         
         r=2
         if( Center =='A') :
            
            r=0
            if( b==c  and  type=='O'):# result would be orthorhombic primitive
               return None
            
         elif( Center =='B'):
         
            r=1
            if( a==c and  type=='O'):
               return None
            
         elif( a==b  and  type=='O'):
            return None
         
         k=0
	
         Res[r,0]= ResP[r,0]
         Res[r,1]= ResP[r,1]
         Res[r,2]= ResP[r,2]
         for i in range(1,3):
           
            if( k==r):
               k=k+1
            for  cc in range(3) :       
            
               R = (r+1)%3
               s =   (-1)**i
               
               Res[k,cc]= ResP[(R)%3,cc]/2+s*ResP[(R+1)%3,cc]/2            
            
            k=k+1
        
         Res=Res.I
      
      
      
      elif( Center =='R'):
      
         if( type != 'H' or alpha >120):#alpha =120 planar, >120 no go or c under a-b plane.
          
            self.conventionalUB=NiggliUB = None
            return None
         
         
         Alpha = alpha*math.pi/180
         Res[0,0] = a
         Res[1,0] =(a*math.cos( Alpha ))
         Res[1,1] = (a*math.sin( Alpha ))
         Res[2,0] =(a*math.cos( Alpha ))
         Res[2,1] =(a*Res[1,0] -Res[2,0]*Res[1,0])/Res[1,1]
         Res[2,2] =math.sqrt( a*a- Res[2,1]*Res[2,1]-Res[2,0]*Res[2,0])
        
         Rhomb2Hex= matrix([[1. ,-1., -1.],[-2. ,-1., -1.],[1. ,2., -1.]])
         Rhomb2Hex =(1./3.)*Rhomb2Hex
      
      
    
      if( numpy.linalg.det( Res )< 0):
          for  cc in range(3):
             Res[0,cc] *=-1
# TODO    
#      Res = DataSetTools.components.ui.Peaks.subs.Nigglify( Res )
      
      Res = self.Niggli(Res)
      return Res
      
   def Perturb( self,val, error):
      return val+random.random()*error-error/2
      
   def Next( self, hkl1):
      #print "Next"
      hkl=matrix([[hkl1[0,0]],[hkl1[1,0]],[hkl1[2,0]]])
      S =(math.fabs( hkl[0,0])+math.fabs( hkl[1,0])+math.fabs( hkl[2,0]))
      #print ["S=",S]
      #The sum of abs hkl's = S until not possible. Increasing lexicographically 
      if( hkl[2,0] < 0):
         #print "Nexta"
         hkl[2,0] = -hkl[2,0]
         #print hkl
         return hkl
     
      if( math.fabs( hkl[0,0])+ math.fabs( hkl[1,0]+1 ) <= S):
      
         #print "Nextb"
         hkl[1,0] +=1
         hkl[2,0] = -(S -math.fabs( hkl[0,0])- math.fabs( hkl[1,0] ))
      elif( math.fabs( hkl[0,0]+1 ) <= S):
         
         #print "Nextc"
         hkl[0,0]=  hkl[0,0]+1.0
         hkl[1,0] = -(S - math.fabs( hkl[0,0]))
         hkl[2,0] = 0
      else:
         
         #print "Nextd"
         hkl[1,0]=0
         hkl[2,0]=0
         hkl[0,0] = -S-1
      #print hkl
      return hkl
      
   def FixLatParams( self,List):
      npos=0
      nneg=0
      if len(List)<6:
         return List
      has90=False
      for i in range(3,6):       
        if math.fabs(List[i]-90)<.00001:
           nneg  =nneg+1
           has90=True
        elif List[i] <90:
           npos=npos+1
        else:
           nneg=nneg+1
      over90=False
      if nneg > npos or has90:
         over90= True  
      
      for i in range(3,6):
         if  List[i]>90 and not over90:
            List[i]=180-List[i]
         elif List[i]<90 and over90:
            List[i]=180-List[i]
         
      bdotc = math.cos(List[3]/180.*math.pi)*List[1]*List[2]
      adotc= math.cos(List[4]/180.*math.pi)*List[0]*List[2]
      adotb= math.cos(List[5]/180.*math.pi)*List[1]*List[0]
      if List[0] > List[1] or (List[0] == List[1] and math.fabs(bdotc)>math.fabs(adotc)):
        List = self.XchangeSides( List,0,1)
      bdotc = math.cos(List[3]/180.*math.pi)*List[1]*List[2]
      adotc= math.cos(List[4]/180.*math.pi)*List[0]*List[2]
      adotb= math.cos(List[5]/180.*math.pi)*List[1]*List[0]
      if List[1] > List[2] or (List[1] == List[2] and math.fabs(adotc)>math.fabs(adotb)):
        List = self.XchangeSides(List,1,2)
      bdotc = math.cos(List[3]/180.*math.pi)*List[1]*List[2]
      adotc= math.cos(List[4]/180.*math.pi)*List[0]*List[2]
      adotb= math.cos(List[5]/180.*math.pi)*List[1]*List[0]
      
      if List[0] > List[1] or (List[0] == List[1] and math.fabs(bdotc)>math.fabs(adotc)):
         List = self.XchangeSides( List,0,1)        
     
      return List
        
   def FixUpPlusMinus( self, UB):#TODO make increasing lengthed sides too
      M= matrix([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]])
      M1= matrix([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]])
      G= UB.T*UB
      G.I
      
      if G[0,1]>0:
         if G[0,2]>0:
            if G[1,2]>0:
               return UB
            else:
               M[1,1]=M[2,2]=-1
         elif G[1,2]>0:
            M[0,0]=M[2,2]=-1
         else:
            M[1,1]=M[0,0]=-1
      else:
         if G[0,2]>0:
            if G[1,2]>0:
              M[1,1]=M[0,0]=-1
            else:
              M[0,0]=M[2,2]=-1
         elif G[1,2]>0:
            M[2,2]=M[1,1]=-1
         else:
            return UB
    
      
      return UB*M
      
         
             
   def getPeaks( self,Inst,UB, error,Npeaks):
      
      CreatePeaksWorkspace(InstrumentWorkspace="Sws",NumberOfPeaks=0,OutputWorkspace="Peaks")
      Peaks=mtd["Peaks"]

      #BankNames=["bank17","bank18","bank22","bank26","bank27","bank28","bank33","bank36","bank37","bank38","bank39","bank47"]
      #for i in  range(Peaks.getNumberPeaks()):
      #     Peaks.removePeak(0)
      MinAbsQ = 100000000
      UBi= matrix([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]])
  
      for ii in range(3):
         for jj in range(ii,3):
     
            UBi = UB[ii,jj]
            if( math.fabs( UBi ) < MinAbsQ  and  UBi !=0):
               MinAbsQ =  math.fabs(UBi )
     
      hkl=matrix([[0.0],[0.0],[0.0]])
     
      Error = error*MinAbsQ
      npeaks=0
      
              
      a1= hkl[0,0]
      a2=hkl[1,0]
      a3=hkl[2,0]
      done = False      
      while not done:
        
        
        Qs = (UB*hkl)
        Qs=Qs*(2*math.pi)
 
        for qs in range(3):          
          Qs[qs,0] = self.Perturb(Qs[qs,0],Error)
          #Qs[qs] = 2*math.pi*Qs[qs]      
          
          
        if( Qs is not None  and  Qs[2,0] > 0):
	       #QQ= numpy.array([Qs[0,0],Qs[1,0],Qs[2,0]])
         QQ = mantid.kernel.V3D(Qs[0,0],Qs[1,0],Qs[2,0])
         norm = QQ.norm()
        
        
         if norm>.3 and   norm < 30: 
           peak =Peaks.createPeak(  QQ, 1.0) 
           #print ["QQ=",QQ.norm(), npeaks, hkl[0,0],hkl[1,0],hkl[2,0]]
           peak.setQLabFrame(mantid.kernel.V3D(Qs[0,0],Qs[1,0],Qs[2,0]),1.0)
        
           Peaks.addPeak(peak)
           npeaks = npeaks+1
           
 
        hkl = self.Next( hkl)
        if npeaks>= Npeaks:
          done =True
        if math.fabs(hkl[0,0])>15:
          done = True
        if  math.fabs(hkl[1,0])>15:
          done = True
        if math.fabs(hkl[2,0])>15:
         done = True
    
        
     
      return Peaks
      
        
   def newSetting( self, side1,side2,Xtal,Center,ang, i1,i2a):
      if( Xtal=='O'):
        if(  ang>20 or i1>0 or i2a >1):
          return False
        else:
         return True
      if(Xtal=='H'):
         if side2>0 or i2a>1 or not(Center=='P' or Center=='I'):
           return False
         else:
          return True
      if( Xtal!='M'):
         return False
      return True
      
   def MonoClinicRearrange(self, Sides,Xtal,Center, i1,i2a):
      i1q =i1
      i2q = (i1+i2a)%3
      i3q=(i2q+1)%3
      if( i1q==i3q):
          i3q = (i3q+1)%3
      a = Sides[i1q]
      b= Sides[ i2q]
      c = Sides[i3q]
      
      return [a,b,c]
      
   def getMatrixAxis( self,v, Xtal):
      ident= matrix([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]])
      if Xtal !='H' or v>=2:
         return ident
      ident[v,v] =0
      ident[2,2] =0
      v1= 2
      ident[v,v1] =1
      ident[v1,v] =1	
      return ident 
    
   def getLat( self, UB):
      G=UB.T*UB
      G1=G.I
      Res=[math.sqrt(G1[0,0]),math.sqrt(G1[1,1]),math.sqrt(G1[2,2])]
      Res.append(math.acos( G1[1,2]/Res[1]/Res[2])*180.0/math.pi)
      Res.append(math.acos( G1[0,2]/Res[0]/Res[2])*180.0/math.pi)
      Res.append(math.acos( G1[0,1]/Res[0]/Res[1])*180.0/math.pi)
      return Res
   def AppendForms( self, condition, Center,CenterTarg, FormNums, List2Append):
      L= List2Append
      if condition and Center != CenterTarg:
        for i in range(len(FormNums)):
            L.append(FormNums[i])
      elif Center ==CenterTarg:
        for i in range(len(FormNums)):
            L.append(FormNums[i])
      return L
      
   def Xlate(self,Xtal,Center,sides,LatNiggle): #sides are sides of conventional cell
      if Xtal=='O':
        C=Center
        if sides[0] == sides[1]:
           if sides[1]==sides[2]:
              X="Cubic"
              Z1=list(self.Cubic)
           else:
              X="Tetragonal"
              Z1=list(self.Tetr)
        elif sides[0]==sides[2]:
           X="Tetragonal"
           Z1=list(self.Tetr)
        elif  sides[1]==sides[2]:
           X="Tetragonal"           
           Z1=list(self.Tetr)
        else:
           X="Orthorhombic"
           Z1=list(self.Orth)
        if C=='A' or C =='B':
           C ='C'
      elif Xtal=='H':
        if Center =='I':
           C ='R'
           X='Rhombohedral'
           Z1=list(self.Hex)
        else:
          C='P'
          X="Hexagonal"
          Z1=list(self.Hex)
      else:#Monoclinic
         X="Monoclinic"
         Z1=list(self.Mon)
         C=Center
         LL=[math.cos(LatNiggle[5]/180*math.pi)*LatNiggle[0]*LatNiggle[1], math.cos(LatNiggle[4]/180*math.pi)*LatNiggle[0]*LatNiggle[2],math.cos(LatNiggle[3]/180*math.pi)*LatNiggle[2]*LatNiggle[1]]
        
         if C=='A' or C =='B':
           C ='C'
           
         if C=='C' or C=='I':#'I':
            
           Z1=self.AppendForms( LatNiggle[2]*LatNiggle[2]<4*math.fabs(LL[2]), 'C',C,[10,14,39], Z1)
           Z1=self.AppendForms( LatNiggle[0]*LatNiggle[0]<4*math.fabs(LL[1]), 'C',C,[20,25,41], Z1)
           
           Z1=self.AppendForms( LatNiggle[1]*LatNiggle[1]<4*math.fabs(LL[2]), 'C',C,[37], Z1)
          
           Z1=self.AppendForms( 3*LatNiggle[0]*LatNiggle[0] < LatNiggle[2]*LatNiggle[2]+2*math.fabs(LL[1]), 'I',C,[17], Z1)
           Z1=self.AppendForms( 3*LatNiggle[1]*LatNiggle[1]<  LatNiggle[2]*LatNiggle[2]+2*math.fabs(LL[2]), 'I',C,[27], Z1)
           
      if( C=='P'):
           Z2=self.CentP
      elif C=='F':
           Z2=self.CentF
      elif C=='I' or C=='R':
           Z2=self.CentI
      elif C=='C':
           Z2=self.CentC
      Z1=sorted(Z1)
      return [X,C, Z1, Z2]
      
   
   
   def MatchXtlparams( self, List1a, List2, tolerance, message):
      List1=List1a
      print "standardized lists="
      print List1
      print List2 
      self.assertEqual(len(List1a),6,"Not the correct number of Xtal parameters")
      self.assertEqual(len(List2),6,"Not the correct number of Xtal parameters")
      Var=["a","b","c","alpha","beta","gamma"]      
      self.assertDelta( List1[0],List2[0],tolerance, message +"for "+Var[0])                
      self.assertDelta( List1[1],List2[1],tolerance, message +"for "+Var[1])              
      self.assertDelta( List1[2],List2[2],tolerance, message +"for "+Var[2])
      if List1[0] >List1[1]-.0001:  
         if List1[1]>List1[2]-.001:   # 3 equal sides
            match = False
            print "in Three = sides case"
            i=0
            for i in range(0,3):
               match= math.fabs(List1[3]-List2[3])<tolerance and  math.fabs(List1[4]-List2[4])<tolerance and  math.fabs(List1[5]-List2[5])<tolerance 
               if match:
                  break
               List1=self.XchangeSides( List1,1,0)
               match= math.fabs(List1[3]-List2[3])<tolerance and  math.fabs(List1[4]-List2[4])<tolerance and  math.fabs(List1[5]-List2[5])<tolerance 
               if match:
                  break
               
               List1=self.XchangeSides( List1,1,2)
            self.assertTrue( match,"Angles do not match in any order")
         else:
           self.assertDelta( List1[5],List2[5],tolerance,"Error in "+Var[5])
           if math.fabs(List1[3]-List2[3])>tolerance:
              List1 = self.XchangeSides( List1,0,1)
           self.assertDelta( List1[3],List2[3],tolerance,"Error in "+Var[3])
           self.assertDelta( List1[4],List2[4],tolerance,"Error in "+Var[4])
      elif List1[1]> List1[2]-.001:
         self.assertDelta(List1[3],List2[3],tolerance,"Error in "+Var[3])
         if math.fabs(List1[4]-List2[4])>tolerance:
            List1= self.XchangeSides(List1,1,2)
         
         self.assertDelta(List1[4],List2[4],tolerance,"Error in "+Var[5])
         
         self.assertDelta(List1[5],List2[5],tolerance,"Error in "+Var[5])
      else:
         self.assertDelta(List1[3],List2[3],tolerance,"Error in "+Var[3])
                  
         self.assertDelta(List1[4],List2[4],tolerance,"Error in "+Var[5])
         
         self.assertDelta(List1[5],List2[5],tolerance,"Error in "+Var[5])
     
         
   def XchangeSides( self, Lat1, s1,s2):
      Lat=list(Lat1)
      if s1<0 or s2<0 or s1>=3 or s2>2 or s1==s2:
         return Lat
      sav=Lat[s1]
      Lat[s1]=Lat[s2]
      Lat[s2]=sav
      sav=Lat[s1+3]
      Lat[s1+3]=Lat[s2+3]
      Lat[s2+3]=sav
      
      return Lat
   def GetConvCell( self,Peaks,XtalCenter1,wsName, nOrigIndexed,tolerance,matchLat):  
    #SelectCellOfType(Peaks,XtalCenter1[0],XtalCenter1[1],True,.05)
                  #CopySample(Peaks,"Sws",CopyMaterial="0",CopyEnvironment="0",CopyName="0",CopyShape="0",CopyLattice="1")
                  #OrLat= mtd["Sws"].sample().getOrientedLattice()
        CopySample(Peaks,wsName,CopyMaterial="0",CopyEnvironment="0",CopyName="0",CopyShape="0",CopyLattice="1")
        FormXtal=XtalCenter1[2]
        FormCenter= XtalCenter1[3]
        i1=0
        i2=0
        Lat0= self.FixLatParams( matchLat)
        while i1< len(FormXtal) and i2 < len(FormCenter):
           if FormXtal[i1]<FormCenter[i2]:
              i1=i1+1
           elif FormXtal[i1]>FormCenter[i2]:
               i2=i2+1
           else:
               Res=SelectCellWithForm(Peaks, FormXtal[i1],True)
               print ["#i1,orig indexed,Sel Res=",i1,nOrigIndexed,Res]
               if Res[0] > .85* nOrigIndexed:
                 CopySample(Peaks,"Temp",CopyMaterial="0",CopyEnvironment="0",CopyName="0",CopyShape="0",CopyLattice="1")
                 OrLat= mtd["Temp"].sample().getOrientedLattice()                  
                 Lat1= [OrLat.a(),OrLat.b(),OrLat.c(),OrLat.alpha(),OrLat.beta(),OrLat.gamma()]
                 Lat1 = self.FixLatParams(Lat1)
                 print ["Formnum,Lat1,Lat0",i1,Lat1,Lat0]
                 if  math.fabs(Lat0[0]-Lat1[0])<tolerance and math.fabs(Lat0[1]-Lat1[1])<tolerance and math.fabs(Lat0[2]-Lat1[2])<tolerance:
                     
                     for i in range(3):
                        if math.fabs(Lat0[3]-Lat1[3])<tolerance and math.fabs(Lat0[4]-Lat1[4])<tolerance and math.fabs(Lat0[5]-Lat1[5])<tolerance:
                           break
                        if Lat1[0]>Lat1[1]-.0001:
                           Lat1=self.XchangeSides( Lat1,0,1)
                           print ["a",Lat1]
                        if math.fabs(Lat0[3]-Lat1[3])<tolerance and math.fabs(Lat0[4]-Lat1[4])<tolerance and math.fabs(Lat0[5]-Lat1[5])<tolerance:
                           break
                        if Lat1[1]>Lat1[2]-.0001:
                           Lat1=self.XchangeSides( Lat1,1,2)
                           print ["b",Lat1]
                        if math.fabs(Lat0[3]-Lat1[3])<tolerance and math.fabs(Lat0[4]-Lat1[4])<tolerance and math.fabs(Lat0[5]-Lat1[5])<tolerance:
                           break
                        print ["c",Lat1]
                     if math.fabs(Lat0[3]-Lat1[3])<tolerance and math.fabs(Lat0[4]-Lat1[4])<tolerance and math.fabs(Lat0[5]-Lat1[5])<tolerance:                          
                          return Lat1
                 i1=i1+1
                 i2=i2+1        
                 CopySample(wsName, Peaks,CopyMaterial="0",CopyEnvironment="0",CopyName="0",CopyShape="0",CopyLattice="1")       
        return []
                 
           
   def runTest(self):
   
      CreateSingleValuedWorkspace(OutputWorkspace="Sws",DataValue="3")
      
      CreateSingleValuedWorkspace(OutputWorkspace="Temp",DataValue="3")
      LoadInstrument(Workspace="Sws",InstrumentName="TOPAZ")
      Inst= mtd["Sws"].getInstrument()
      startA = 2
      side1Ratios =[1.0,1.2,3.0,8.0]
      alphas =[20,50,80,140,110]
      xtal=['M','O','H']
      centerings=['A','I','P','F','C','B']
      error=[0,.05,.1,.15]
      Npeaks=150
      for Error in error:
       for side1 in range(4):
        for side2 in range(side1,4):
         for Xtal in xtal:
          for Center in centerings:
           for ang in alphas:
            for i1 in range(3):
             for i2a in range(1,3):
               if self.newSetting( side1,side2,Xtal,Center,ang, i1,i2a):
                        
                  Sides=[startA, startA*side1Ratios[side1],startA*side1Ratios[side2]]
                  print [Sides,Error,Xtal,Center,ang,i1,i2a]
                  Sides= self.MonoClinicRearrange( Sides,Xtal,Center,i1,i2a)
                  x=Peak2ConvCell_Test()
                  
                  UBconv= self.CalcConventionalUB(startA, startA*side1Ratios[side1],startA*side1Ratios[side2],ang,ang,ang,Xtal)	
                  
                  UBnig= self.CalcNiggliUB(Sides[0],Sides[1],Sides[2],ang,ang,ang,Xtal,Center)
                  
                  UBconv = self.conventionalUB
                  V =self.getMatrixAxis( i1,Xtal)
                  if  UBconv == None:			    
                   continue
                  if UBnig==None:
                   continue
                  UBnig= V*UBnig
                  UBconv = V*UBconv
                  
                  UBnig = self.FixUpPlusMinus(UBnig)
                  UBconv= self.FixUpPlusMinus(UBconv)
                  print "-------Conv, nig,Nig lat, Calc Lat------------"
                  print UBconv
                  print UBnig
                  Lat0= self.getLat(UBnig)
                  print Lat0
                  #Need to get a*.b* etc all positive or all negative
                  Peaks=self.getPeaks(Inst,UBnig, Error,Npeaks)
                  FindUBUsingFFT(Peaks,.3,15,.15)
                  InPks=IndexPeaks(Peaks,.10)
                  print ["#indexed=",InPks[0]]
                  CopySample(Peaks,"Sws",CopyMaterial="0",CopyEnvironment="0",CopyName="0",CopyShape="0",CopyLattice="1")
                  OrLat= mtd["Sws"].sample().getOrientedLattice()
                  
                  Lat1= [OrLat.a(),OrLat.b(),OrLat.c(),OrLat.alpha(),OrLat.beta(),OrLat.gamma()]
                  print "       --- conv latt,Calc Convlatt------"
                  Lat1=self.FixLatParams(Lat1)
                  print Lat1
                  Lat0=self.FixLatParams(Lat0)
                  print Lat1
                  print Lat0
                  self.MatchXtlparams( Lat1, Lat0, .03, "Niggli values do not match")
                 
                  
                  #Now see if the conventional cell is in list
                  XtalCenter1= self.Xlate(Xtal,Center,Sides,Lat0) #get proper strings for SelectCellOfType
                  print ["Xtal/Center=",XtalCenter1]
                  #SelectCellOfType(Peaks,XtalCenter1[0],XtalCenter1[1],True,.05)
                  #CopySample(Peaks,"Sws",CopyMaterial="0",CopyEnvironment="0",CopyName="0",CopyShape="0",CopyLattice="1")
                  #OrLat= mtd["Sws"].sample().getOrientedLattice()
                  Lat0= self.getLat(UBconv)
                  Lat0=self.FixLatParams(Lat0)
                  Lat1 = self.GetConvCell( Peaks,XtalCenter1,"Sws",InPks[0],.03,Lat0)
                  print Lat0
                  
                  
                  Lat1=self.FixLatParams(Lat1)
                  print Lat1                 
                  print "------------------------------------------------------------------"
                  self.MatchXtlparams( Lat1, Lat0, .03, "Conventional lattice parameter do not match")
                  self.assertTrue( len(Lat1)>4,"Conventional values do not match")
                  #self.assertDelta( OrLat.b(),Lat0[1],.03,"Conventional b values do not match")
                  #self.assertDelta( OrLat.c(),Lat0[2],.03,"Conventional c values do not match")
                  #self.assertDelta( OrLat.alpha(),Lat0[3],.03,"Conventional alpha values do not match")
                  #self.assertDelta( OrLat.beta(),Lat0[4],.03,"Conventional beta values do not match")
                  #self.assertDelta( OrLat.gamma(),Lat0[5],.03,"Conventional gamma values do not match")
   def requiredFiles(self):
      return ["XXX"]
   	   
	      
#Peaks=WorkspaceFactoryImpl.createPeaks(WorkspaceFactoryImpl.Instance())
#LoadIsawPeaks(Filename="/usr2/DATA/Projects/TOPAZ/TOPAZ_3007Bank17.peaks",OutputWorkspace="AbcD")
#Peaks=mtd["AbcD"]      
   
#x=Peak2ConvCell_Test() 
#print x.XchangeSides([1,2,3,20,30,40],2,0)
#x.runTest()
#M=matrix([[  0.00000000e+00 , 5.00000000e-01, 5.00000000e-01],[  5.00000000e-01, 5.00000000e-01 , -6.84982935e-17],[ -7.77861913e-01,  1.81985117e-01 , -5.95876796e-01]])
#print x.Niggli(M)
#print x.CalcConventionalUB(2.0, 2.0,2.0,110.,110. , 110.,'M')

#print x.CalcNiggliUB(2.0, 2.0,2.0,110.,110. , 110.,'M','P')
#print x.conventionalUB
#------------------Need help adding created peak to Analysis 
#  ---------------Data Service to be used in algorithms------

#AnalysisDataServiceImpl.addOrReplace("abcdef",Peaks)
#print ["name=",AnalysisDataServiceImpl.Instance().size()]
#-------Help cannot load yet------


#x.getPeaks(Peaks,x.CalcNiggliUB(2.0, 2.0,3.0,110., 20., 30.,'O','I'),.05,30,100000,3557)

#Load(Filename="/usr2/DATA/TOPAZ/TOPAZ_5689_event.nxs",OutputWorkspace="XX")
#LoadInstrument(Workspace="XX", InstrumentName="TOPAZ")
#Inst= mtd["XX"].getInstrument()
#LoadIsawPeaks(Filename="/usr2/DATA/Projects/TOPAZ/TOPAZ_3007Bank17.peaks",OutputWorkspace="AbcD")
#Peaks=mtd["AbcD"]      
# does not work Inst = Peaks.getInstrument()
#peak = Peaks.getPeak(3)
#detID= peak.getDetectorID()
#det = Inst.getDetector(detID)
#Bank22= Inst.getComponentByName("bank22")
#UB=x.CalcNiggliUB(2.0, 2.0,3.0,110., 20., 30.,'O','I')
#Peaks=x.getPeaks( Inst,UB, .05,150)
#print Peaks.getPeak(0)
#FindUBUsingFFT(Peaks,.3,15,.15)
#Peaks.setName("abcd")
#print Peaks.mutableSample().getOrientedLattice()
