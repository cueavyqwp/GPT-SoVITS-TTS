import traceback
import hashlib
import shutil
import os

import requests
import gradio

cwd = os.path.dirname( __file__ )
output =  os.path.join( cwd , "output" )
file_path = f"/file/extensions/{ os.path.split( cwd )[ 1 ] }/output"
if not os.path.exists( output ) :  os.mkdir( output )

params = {
    "api" : "http://127.0.0.1:9880",
    "language" : "auto" ,
    "autoplay" : True
}

def clear_output() -> None :
    shutil.rmtree( output )
    os.mkdir( output )

def output_modifier( text : str ) -> str :
    try :
        file_name = f"{ hashlib.sha256( text.encode() ).hexdigest() }.wav"
        path = os.path.join( output , file_name )
        if not os.path.exists( path ) :
            respones = requests.post( params[ "api" ] , json = { "text_language" : params[ "language" ] , "text" : text } )
            assert respones.ok , f"request error: { respones.status_code }"
            with open( path , "wb" ) as fp : fp.write( respones.content )
        text += f"<p><audio src='{ file_path }/{ file_name }' controls { 'autoplay' if params[ 'autoplay' ] else '' }></audio></p>"
    except :
        print( traceback.format_exc() )
    return text

def history_modifier( history : dict[ str , list[ list[ str ] ] ] ) -> dict[ str , list[ list[ str ] ] ] :
    if len( history[ "internal" ] ) : history[ "visible" ][ -1 ][ -1 ] = history[ "visible" ][ -1 ][ -1 ].replace( "autoplay" , "" )
    return history

def ui() -> None :
    with gradio.Accordion( "GPT-SoVITS-TTS" ) :
        with gradio.Row() :
            autoplay = gradio.Checkbox( value = params[ "autoplay" ] , label = "autoplay" )
            api = gradio.Textbox( value = params[ "api" ] , label = "GPT-SoVITS API url" )
            language = gradio.Textbox( value = params[ "language" ] , label = "language" )
        with gradio.Row() :
            clear_cache = gradio.Button( value = "Clear cache"  )
    autoplay.change( lambda value : params.update( { "autoplay" : value } ) , autoplay )
    api.change( lambda value : params.update( { "api" : value } ) , api )
    language.change( lambda value : params.update( { "language" : value } ) , language )
    clear_cache.click( clear_output )
