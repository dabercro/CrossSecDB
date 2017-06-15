import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.parseArguments()

process = cms.Process('GENXSEC')

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000000

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(options.inputFiles),
    duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
)

process.genxsec = cms.EDAnalyzer('GenXSecAnalyzer')

process.path = cms.Path(process.genxsec)
