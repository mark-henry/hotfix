# Hotfix Helper #

This suite of utilities takes in a hotfix specifications document of the form:

	<hotfix>
		<title>RPE 3.5.2 Hotfix 7</title>
		<build>RPE-3.5.2.25-HF7-148</build>
		<web>10.1.0.180</web>
		<app>10.1.0.178</app>
		<appspecial>Speical App Server instructions</appspecial>
		<offline>10.1.0.179</offline>
		<offlinespecial>Speical App Server instructions</offlinespecial>
		<issue>
			<number>38293</number>
			<summary>Optimized Process Overpayment offline. Child issue 38954 tracks an index script for this issue.</summary>
			<file>20151007_1341_38954_SS.sql</file>
			<file>getStagingData.sql</file>
		</issue>
	</hotfix>

and "compiles" it to an instructions document of the form:

	<instructions>
		<build>RPE-3.5.2.25-HF7-148</build>
		<title>RPE 3.5.2 Hotfix 7</title>
		<issue>
			<number>38293</number>
			<summary>Optimized Process Overpayment offline.</summary>
			<file>20151007_1341_38954_SS.sql</file>
			<file>getStagingData.sql</file>
		</issue>
		<database>
			<script>20150910_0124_39022_SS.sql</script>
			<script>20151006_0513_38983_SS.sql</script>
		</database>
		<businessrules>true</businessrules>
		<app>
			<replacement>
				<filename>ITPCoreBusiness.dll</filename>
				<path>C:\RSI\Web Services\ExternalWebService\bin\ITPCoreBusiness.dll</path>
				<path>C:\RSI\Web Services\NetWebServices\bin\ITPCoreBusiness.dll</path>
				<path>C:\RSI\Web Services\Rules Services\bin\ITPCoreBusiness.dll</path>
			</replacement>
			<restartiis>true</restartiis>
		</app>
	</instructions>

and then "renders" this to an HTML document that's ready to go out to sites.

The initial spec XML can be easily made with the Hotfixhelper frontend web app.


## Installation ##

Following python packages required:
* pip install pystache
* pip install markdown
* pip install xmltodict
