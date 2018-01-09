# LumiraExtensionMigrator
A utility for migrating SAP Design Studio Component extensions to SAP Lumira Designer 2.x.

Prior to 1.6, SAP Design Studio used the SAP UI5 Commons library for rendering applications in the browser.  In 1.6, SAP introduced optional support for the Fiori UX library, also known as SAP UI5 M.  In 2.x, SAP made Fiori the standard application rendering library and removed commons support.  In the components SDK, was a new flag, allowing developers to declare whether their components were compatible with Commons only, M only, or both; via an xml attribute called “*modes*”.  Since Design Studio was Commons only prior to 1.6 and in 1.6, this was still the default (and most common) mode for applications and this is the default, if *modes* is missing.  This clause was maintained in 2.x, even though Commons support was dropped.  

When designing a component, the developer can choose whether it is a native UI5 component, or whether they will start from scratch, with an empty div and use their favorite javascript libraries.  This is what my [SDK tutorial ][1]does and is by far the most common approach for custom components.  These components usually don’t care which version of UI5 is used, because they don’t use it.  The most commonly seen native UI5 components are in the Community SDK Components.

**There are a few possible ways that this can affect a component:**

- The component has been created since 1.6 was released and was originally built to be compatible with both M and Commons.  It works as is under 2.x.

- The component was created before 1.6, but is actively maintained and the creator has released an updated version, compatible with both M and Commons.  It works as is under 2.x.  E.g., there is a 2.0 version of the community [SDK Components][5].

- The component was built for 1.6 and is compatible with Commons only and the developer made an explicit statement to this effect.  This usually happens when the component is a native UI5 component and the developer only created a version for commons.  You are out of luck, unless the developer updates it.  

- The component was originally built with 1.5 or earlier and is a native UI5 component and never updated.  This specific use case was the reason for the default modes was commons and is really the same as the scenario above.  

- The component was created under 1.6 and is not a native UI5 component, but the developer explicitly declared modes as supporting Commons only.  This should be very rare.

- The component is not a native UI5 component and was either created prior to 1.6, or the developer never bothered to make a modes declaration.  In principle, most such components should not have a problem and can probably run under 2.x with only a metadata tweak; adding a modes declaration.  

Many older components that should have no problem running in 2.x can’t, simply because of a missing modes declaration.  

## The Lumira Extension Migrator

If your component extensions falls into the category of components which could theoretically be migrated without a rewrite, you have a couple of options.  The absolute best approach, if you have access to the original eclipse project, is to tweak the modes attribute yourself in contribution.xml and [create a new installer][4], taking care to test exhaustively.  If you don’t have access to the original development project and only have the .zip installer file, you can use the Lumira Extension Migrator, an open source (Apache 2.0 license) migration utility.  

## The Lumira Extension Migrator is a utility which can do two things:

It can analyze a Design Studio/Lumira Designer component extensions installer zip and report on which components are already 2.x compatible, which are not but can be migrated and which ones can’t be automatically migrated.  

It can create a copy of the installer .zip, modified to include the modes tweak on suitable components.  

## Getting the Lumira Extension Migrator

Clone it using git utilities, or manually download it.  The utility itself is Migrate.py.  You will need [Python][2] installed, in order to execute this utility.  It was written with Python 3, as Python 2.x is nearing its EOL date, so you need the latest version of Python 3.x to run it.  

The extension migrator is a command line utility.  Once you have it downloaded, open the command prompt migrate to its directory to execute it.  To review the command line options, type to following command in:

`Python Migrate.py -h`

## Reporting with the Lumira Extension Migrator

`Python Migrate.py –r`

If executed with the –r (reporting) option, Migrate.py will survey the installed extensions and report on their status.  This will help you plan your next steps.

## Automated migration with the Lumira Extension Migrator

To migrate an installer, you need three command line parameters.  

**-f ** The folder path, where the file to be migrated is located.
**-s ** The source file.
**-t**  The target file.

For example, the [Design Studio 1.4 SDK samples ][3]are not 2.x compatible, because the modes attribute did not exist then.  Suppose I have an installer .zip, named DeployableSDKSamples14old.zip, in my Downloads folder.  Seven of the 18 components in the 1.4 samples are UI5 based and can’t be migrated.  The other 11 can be and I want to make them 2.x compatible.   I might do the following:

`Python Migrate.py -f "C:\Users\dave\Downloads" -s "DeployableSDKSamples14old" -t "DeployableSDKSamples14"`

You can explicitly write the .zip extension in the names, or leave it out.  If it is left out, then it is implied.

When executing the command, I’d see the following:
	`Sparkline metadata modified to be Lumira 2.x compliant.`
  `Colored Box metadata modified to be Lumira 2.x compliant.`
	`Exception Icon metadata modified to be Lumira 2.x compliant.`
	`KPI Tile metadata modified to be Lumira 2.x compliant.`
	`Simple Crosstab metadata modified to be Lumira 2.x compliant.`
	`Video metadata modified to be Lumira 2.x compliant.`
	`Clock metadata modified to be Lumira 2.x compliant.`
	`Audio metadata modified to be Lumira 2.x compliant.`
	`Timer metadata modified to be Lumira 2.x compliant.`
	`Simple Table metadata modified to be Lumira 2.x compliant.`
	`Application Header is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`Color Picker is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`Formatted Text View is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`Paginator is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`Progress Indicator is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`Rating Indicator is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`Slider is a UI5 component and can't be automatically migrated.  Left unchanged.`
	`JSON Grabber metadata modified to be Lumira 2.x compliant.`
	`Migrated 11 components`
	`DeployableSDKSamples14.zip created in folder C:\Users\dave\Downloads, with SAP UI5 modes commons and m.
	  Uninstall the original from the Lumira Designer client and the BIP and install the updated version`

## Tips

Uninstall the originals, before installing the new versions.

Make sure you have a backup and don’t make the source and target filenames the same.  This is why I named the 1.4 version DeployableSDKSamples14old.zip and the 2.x version DeployableSDKSamples14.zip, in the file above.

Test!  Test!  Test!  This is a bling migration and should work for components that follow the developer guidelines, but test anyway.

[1]:	https://blogs.sap.com/2015/09/21/your-first-extension-master-page/%20
[2]:	https://www.python.org/downloads/%20
[3]:	http://help.sap.com/businessobject/product_guides/AAD14/en/DS_14_SDK_SAMPLES.zip
[4]:  https://blogs.sap.com/2016/04/20/your-first-extension-part-14-zipit-n-shipit-aka-creating-an-installer/
[5]:  https://blogs.sap.com/2017/08/18/scn-lumira-designer-2.0-sdk-components/
