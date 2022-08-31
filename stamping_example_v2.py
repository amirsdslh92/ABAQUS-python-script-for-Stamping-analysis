# header
from abaqus import *
from abaqusConstants import *
from caeModules import *
Mdb() 
# parameters used in py script
thick = 1.0#mm
width = 5.0#mm
length = 300.0#mm
DbtwDies = 50.0#mm
Dpunch = 48.0#mm
Wholder = 50.0#mm
Rdie = 5.0#mm
Rpunch = 5.0#mm
Rholder = 6.0#mm
GapHP = 6.0#mm
Hpunch = 50.0#mm
Hdie = 50.0#mm
Dshow = 2.0#mm
friCoef = 0.1#
rho = 2.7e-9#ton/mm3
mass = thick*width*length*rho/2.0#ton
force = 500.0#N
depth = 100.0#mm
YP = 300.0#Mpa
#create a list of velocities for parametric study
VList = [5000,6000,7000,8000,9000,10000]#mm/s  
ARList = []      #store list of spring back angle
for i in range(0,len(VList)):
    #in each loop, using different velocity
    velocity = VList[i]#mm/s
    #------------ step 1 Static: Hold down -----------------------------
    JobName = str(i)+'Step1_Static'      #create Job name for different model
    ModelName = str(i)+'Step1_Static'      #create model name for different model
    staModel = mdb.Model(name=ModelName)   #create model
    # define the blank part
    s = staModel.ConstrainedSketch(name='blank', sheetSize=200.0)
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(0.0, 0.0), point2=(length/2.0, width))
    p = staModel.Part(name='blank', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    # define the holder part
    s = staModel.ConstrainedSketch(name='holder', sheetSize=200.0)
    s.setPrimaryObject(option=STANDALONE)
    tempW = Dpunch/2.0+GapHP
    g1 = s.Line(point1=(tempW, Hpunch), point2=(tempW, 0.0))
    g2 = s.Line(point1=(tempW, 0.0), point2=(tempW+Wholder, 0.0))
    g3 = s.Line(point1=(tempW+Wholder, 0.0), point2=(tempW+Wholder, Hpunch))
    s.FilletByRadius(radius=Rholder, curve1=g2, nearPoint1=(tempW+Wholder, 
        0.0), curve2=g3, nearPoint2=(tempW+Wholder, 0.0))
    p = staModel.Part(name='holder', dimensionality=THREE_D, 
        type=ANALYTIC_RIGID_SURFACE)
    p.AnalyticRigidSurfExtrude(sketch=s, depth=Dshow)
    s.unsetPrimaryObject()
    # define the punch part
    s = staModel.ConstrainedSketch(name='punch', sheetSize=200.0)
    s.setPrimaryObject(option=STANDALONE)
    g1 = s.Line(point1=(0.0, 0.0), point2=(Dpunch/2.0, 0.0))
    g2 = s.Line(point1=(Dpunch/2.0, 0.0), point2=(Dpunch/2.0, Hpunch))
    s.FilletByRadius(radius=Rpunch, curve1=g1, nearPoint1=(Dpunch/2.0, 
        0.0), curve2=g2, nearPoint2=(Dpunch/2.0, 0.0))
    p = staModel.Part(name='punch', dimensionality=THREE_D, 
        type=ANALYTIC_RIGID_SURFACE)
    p.AnalyticRigidSurfExtrude(sketch=s, depth=Dshow)
    s.unsetPrimaryObject()
    # define the die part
    s = staModel.ConstrainedSketch(name='die', sheetSize=200.0)
    s.setPrimaryObject(option=STANDALONE)
    tempH, tempW = -thick - Hdie, DbtwDies/2.0 + Wholder
    g1 = s.Line(point1=(DbtwDies/2.0, tempH), point2=(DbtwDies/2.0, -thick))
    g2 = s.Line(point1=(DbtwDies/2.0, -thick), point2=(tempW, -thick))
    s.FilletByRadius(radius=Rdie,curve1=g1,nearPoint1=(DbtwDies/2.0,-thick),
        curve2=g2, nearPoint2=(DbtwDies/2.0, -thick))
    p = staModel.Part(name='die', dimensionality=THREE_D, 
        type=ANALYTIC_RIGID_SURFACE)
    p.AnalyticRigidSurfExtrude(sketch=s, depth=Dshow)
    s.unsetPrimaryObject()
    # define the material property
    AluMat = staModel.Material(name='Alu')       
    AluMat.Density(table=((2.7e-09, ), ))
    AluMat.Elastic(table=((70000.0, 0.27), ))
    AluMat.Plastic(table=((YP, 0.0), (YP, 1.0)))
    staModel.HomogeneousShellSection(name='SecBlank', material='Alu', 
        thickness=thick)
    p = staModel.parts['blank']
    f = p.faces
    region = regionToolset.Region(faces=f)
    p.SectionAssignment(region=region, sectionName='SecBlank', 
        offsetType=MIDDLE_SURFACE)
    # Define instance, reference points and surface
    a = staModel.rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    inst1 = a.Instance(name='blank', part=staModel.parts['blank'], 
        dependent=ON)
    inst2 = a.Instance(name='die', part=staModel.parts['die'], 
        dependent=ON)
    inst3 = a.Instance(name='holder', part=staModel.parts['holder'], 
        dependent=ON)
    inst4 = a.Instance(name='punch', part=staModel.parts['punch'], 
        dependent=ON)
    inst1.rotateAboutAxis(axisPoint=(0.0, 0.0, 0.0), axisDirection=(
        10.0, 0.0, 0.0), angle=90.0)
    inst1.translate(vector=(0.0, -thick/2.0, 0.0))
    rp1 = a.ReferencePoint(point=(0.0, Hpunch/2.0, 0.0))#punch
    tempW = Dpunch/2.0 + GapHP + Wholder/2.0
    rp2 = a.ReferencePoint(point=(tempW, Hpunch/2.0, 0.0))#holder
    rp3 = a.ReferencePoint(point=(tempW, -Hdie/2.0, 0.0))#die
    rps = a.referencePoints
    rpPunch = a.Set(name='rpPunch', referencePoints=(rps[rp1.id],))
    rpHolder = a.Set(name='rpHolder', referencePoints=(rps[rp2.id],))
    rpDie = a.Set(name='rpDie', referencePoints=(rps[rp3.id],))
    es = inst1.edges
    e = es.findAt(((0.0, -thick/2.0, width/2.0),),)
    symmSet = a.Set(name='SymmX', edges=e)
    surPunch = a.Surface(side2Faces=inst4.faces, name='SurfPunch')
    surHolder = a.Surface(side2Faces=inst3.faces, name='SurfHolder')
    surDie = a.Surface(side1Faces=inst2.faces, name='SurfDie')
    surBlankUp = a.Surface(side2Faces=inst1.faces, name='SurfBlankUp')
    surBlankDown = a.Surface(side1Faces=inst1.faces, name='SurfBlankDown')
    # create step
    step1 = staModel.StaticStep(name='Step-1', previous='Initial', nlgeom=ON)
    step1.Restart(frequency=0, numberIntervals=4, overlay=ON, timeMarks=ON)
    staModel.fieldOutputRequests['F-Output-1'].setValues( numIntervals=4)
    # create interactions and constraints
    staModel.ContactProperty('IntProp-1').TangentialBehavior(
        formulation=PENALTY, table=((friCoef, ), ), fraction=0.005)
    staModel.SurfaceToSurfaceContactStd(name='Int-1', createStepName='Step-1',
        master=surPunch, slave=surBlankUp, sliding=FINITE, thickness=ON, 
        interactionProperty='IntProp-1')
    staModel.SurfaceToSurfaceContactStd(name='Int-2', createStepName='Step-1',
        master=surHolder, slave=surBlankUp, sliding=FINITE, thickness=ON, 
        interactionProperty='IntProp-1')
    staModel.SurfaceToSurfaceContactStd(name='Int-3', createStepName='Step-1',
        master=surDie, slave=surBlankDown, sliding=FINITE, thickness=ON, 
        interactionProperty='IntProp-1')
    staModel.RigidBody(name='Const-1', refPointRegion=rpPunch, 
        surfaceRegion=surPunch)
    staModel.RigidBody(name='Const-2', refPointRegion=rpHolder, 
        surfaceRegion=surHolder)
    staModel.RigidBody(name='Const-3', refPointRegion=rpDie, 
        surfaceRegion=surDie)
    staModel.rootAssembly.engineeringFeatures.PointMassInertia(
        name='Inertia-1', region=rpHolder, mass=mass, alpha=0.0, 
        composite=0.0)
    # mesh the part
    elemType1 = mesh.ElemType(elemCode=S4R, elemLibrary=STANDARD, 
        secondOrderAccuracy=OFF, hourglassControl=ENHANCED)
    p = staModel.parts['blank']
    p.setElementType(regions=(p.faces, ), elemTypes=(elemType1,))
    es = p.edges
    e1 = es.findAt((0.0, width/2.0, 0.0),)
    e2 = es.findAt((length/4.0, 0.0, 0.0),)
    p.seedEdgeBySize(edges=(e2,), size=0.5, constraint=FINER)
    p.seedEdgeByNumber(edges=(e1,), number=2, constraint=FIXED)
    p.setMeshControls(regions=p.faces, elemShape=QUAD, technique=STRUCTURED)
    p.generateMesh()
    # create loads and boundary conditions
    staModel.ConcentratedForce(name='Load-1', createStepName='Step-1', 
        region=rpHolder, cf2=-force)
    staModel.XsymmBC(name='BC-1', createStepName='Initial', region=symmSet)
    staModel.EncastreBC(name='BC-2', createStepName='Initial', region=rpDie)
    staModel.EncastreBC(name='BC-3', createStepName='Initial', region=rpPunch)
    staModel.DisplacementBC(name='BC-4', createStepName='Initial', 
        region=rpHolder, u1=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)
    # create job
    job = mdb.Job(name=JobName, model=ModelName, type=ANALYSIS,
        multiprocessingMode=DEFAULT, numCpus=1, numDomains=1)
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()
    #------------ step 2 Explicit: stampling -----------------------------
    JobName = str(i)+'Step2_Explicit'
    ModelName = str(i)+'Step2_Explicit'
    punchTime = depth/velocity
    expModel = mdb.Model(name=ModelName, objectToCopy=staModel)
    expModel.ExplicitDynamicsStep(name='Step-1', previous='Initial', 
        maintainAttributes=True, timePeriod=punchTime)
    expModel.fieldOutputRequests['F-Output-1'].setValues(numIntervals=8)
    instances = (expModel.rootAssembly.instances['blank'],)
    expModel.InitialState(fileName=str(i)+'Step1_Static', name='PreField', 
        createStepName='Initial', instances=instances)
    expModel.VelocityBC(name='BC-3', createStepName='Initial', region=rpPunch,
        v1=0.0, v2=0.0, v3=0.0, vr1=0.0, vr2=0.0, vr3=0.0)
    expModel.SmoothStepAmplitude(name='Amp', timeSpan=STEP, 
        data=((0.0, 0.0), (punchTime/2.0, 1.0), (punchTime, 0.0)))
    expModel.boundaryConditions['BC-3'].setValuesInStep(
        stepName='Step-1', v2=-velocity, amplitude='Amp')
    job = mdb.Job(name=JobName, model=ModelName, type=ANALYSIS, 
        parallelizationMethodExplicit=DOMAIN, numDomains=1 , numCpus=1,
        multiprocessingMode=DEFAULT)
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()
    #------------ step 3 Static: spring back -----------------------------
    JobName = str(i)+'Step3_Static'
    ModelName = str(i)+'Step3_Static'
    endModel = mdb.Model(name=ModelName, objectToCopy=expModel)
    endModel.StaticStep(name='Step-1', previous='Initial', nlgeom=ON)
    endModel.fieldOutputRequests['F-Output-1'].setValues(numIntervals=8)
    instances = (endModel.rootAssembly.instances['blank'],)
    endModel.predefinedFields['PreField'].setValues(
        updateReferenceConfiguration=ON, fileName=str(i)+'Step2_Explicit')
    for item in endModel.interactions.values():
       item.suppress()
    endModel.EncastreBC(name='BC-1', createStepName='Initial', region=symmSet)
    endModel.EncastreBC(name='BC-2', createStepName='Initial', region=rpDie)
    endModel.EncastreBC(name='BC-3', createStepName='Initial', region=rpPunch)
    endModel.EncastreBC(name='BC-4', createStepName='Initial', region=rpHolder)
    job = mdb.Job(name=JobName, model=ModelName, type=ANALYSIS,
        multiprocessingMode=DEFAULT, numCpus=1, numDomains=1)
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()  
    #============ save data 1: print data in each simulation to a .txt file==============
    #------------ save the S Mises data right after the punch process--------------
    from odbAccess import * 
    o = openOdb(path=str(i)+'Step2_Explicit.odb', readOnly=False)   
    session.viewports['Viewport: 1'].setValues(displayedObject=o)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=8)
    session.writeFieldReport(fileName=str(i)+'S_Mises.txt', append=ON, sortItem='Element Label', 
        odb=o, step=0, frame=8, outputPosition=INTEGRATION_POINT, variable=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), ), 
        {'shell < 5 section points > < ALU >':'SPOS, (fraction = 1.0)'}), ), stepFrame=SPECIFY)
    o.close()
    #============ save data 2: print comparable data to an excel file and draw its figure==============
    #------------ spring back angle calculation -----------------------------
    NodeInfor = ('BLANK', (667,730))
    o = openOdb(path=str(i)+'Step3_Static.odb', readOnly=False)
    a = o.rootAssembly
    j = 0
    setName = 'NSet'+str(j)
    while a.nodeSets.has_key(setName):
        j = j + 1
        setName = 'NSet'+str(j)
    NSet = a.NodeSetFromNodeLabels(name=setName,nodeLabels=(NodeInfor,))
    frame = o.steps['Step-1'].frames[-1]
    fop = frame.fieldOutputs['U']
    fopFromSet = fop.getSubset(region=NSet).values
    Def = []
    for n in range(len(NSet.nodes[0])):
        PreCoord = NSet.nodes[0][n].coordinates
        dispU = fopFromSet[n].data
        Def.append(dispU + PreCoord)
    o.close()
    kValue = abs((Def[1][0]-Def[0][0])/(Def[1][1]-Def[0][1]))
    ARList.append(atan(kValue)/pi*180.0)  
#==== create x-y data ##Punch Velocity - spring back angle for all loops====
MkList = [HOLLOW_CIRCLE, HOLLOW_SQUARE, HOLLOW_DIAMOND, HOLLOW_TRI,
    CROSS, XMARKER, POINT]
dataResult= session.XYData(data=zip(VList, ARList), name='Springback',
    xValuesLabel='Punch Velocity(mm/s)', yValuesLabel='Spring back angle')
curveResult = session.Curve(xyData=dataResult)
curveResult.setValues(displayTypes=(SYMBOL,), useDefault=OFF)
curveResult.symbolStyle.setValues(marker=HOLLOW_SQUARE,size=3.0, color='Black')
curveResults = [curveResult]
#========================generate Velocity - angle plot====================
phPlot1 = session.XYPlot(name='Comparison of Springback')
phPlot1.title.setValues(text='Comparison of Springback')
chartName = phPlot1.charts.keys()[0]
chart = phPlot1.charts[chartName]
chart.setValues(curvesToPlot=curveResults, )
chart.gridArea.style.setValues(color='White')
chart.legend.area.style.setValues(color='Gray')
phPlot1.title.style.setValues(
    font='-*-arial-bold-r-normal-*-*-200-*-*-p-*-*-*')
chart.legend.setValues(show=False)
chart.axes1[0].labelStyle.setValues(
    font='-*-verdana-medium-r-normal-*-*-140-*-*-p-*-*-*')
chart.axes1[0].titleStyle.setValues(
    font='-*-arial-bold-r-normal-*-*-200-*-*-p-*-*-*')
chart.axes2[0].labelStyle.setValues(
    font='-*-verdana-medium-r-normal-*-*-140-*-*-p-*-*-*')
chart.axes2[0].titleStyle.setValues(
    font='-*-arial-bold-r-normal-*-*-200-*-*-p-*-*-*')
#=============================print result to .PNG file=======================
vp = session.viewports['Viewport: 1']
vp.setValues(width=150,height=120,origin=(0,-20))
vp.setValues(displayedObject=phPlot1)
session.printOptions.setValues(rendition=GREYSCALE, vpDecorations=OFF, 
    reduceColors=False)
session.printToFile(fileName='SpringbackCompareVelocity', format=PNG, 
    canvasObjects=( vp, ))