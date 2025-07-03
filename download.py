import argparse
import os
import re
import requests
import signal
import sys
import tempfile
import traceback
import urllib.parse

TAG_REGEX = r"<[^>]+>"
DATE_REGEX = r"\((\d{1,2})/(\d{1,2})/(\d{2,4})\)"

BASE_URL = "https://www.feynmanlectures.caltech.edu"
REFERER = urllib.parse.urljoin(BASE_URL, "flptapes.html")

FLP_PLAYLIST = [
    {
        "title": "<span>#1</span> Atoms in motion (9/26/61)",
        "m4a": "protectedaudio/mp4/FLP_1_01.mp4",
        "oga": "protectedaudio/ogg/FLP_1_01.ogg",
    },
    {
        "title": "<span>#1R</span> Atoms in motion, reconstructed (9/26/2024)",
        "m4a": "protectedaudio/mp4/FLP_1_01R.mp4",
        "oga": "protectedaudio/ogg/FLP_1_01R.ogg",
    },
    {
        "title": "<span>#2</span> Basic physics (9/29/61)",
        "m4a": "protectedaudio/mp4/FLP_2_01.mp4",
        "oga": "protectedaudio/ogg/FLP_2_01.ogg",
    },
    {
        "title": "<span>#3</span> The relation of physics to other sciences (10/3/61)",
        "m4a": "protectedaudio/mp4/FLP_3_01.mp4",
        "oga": "protectedaudio/ogg/FLP_3_01.ogg",
    },
    {
        "title": "<span>#4</span> Conservation of energy (10/6/61)",
        "m4a": "protectedaudio/mp4/FLP_4_01.mp4",
        "oga": "protectedaudio/ogg/FLP_4_01.ogg",
    },
    {
        "title": "<span>#5</span> Time and distance (10/10/61)",
        "m4a": "protectedaudio/mp4/FLP_5_01.mp4",
        "oga": "protectedaudio/ogg/FLP_5_01.ogg",
    },
    {
        "title": "<span>#6</span> Probability (10/13/61)",
        "m4a": "protectedaudio/mp4/FLP_6_01.mp4",
        "oga": "protectedaudio/ogg/FLP_6_01.ogg",
    },
    {
        "title": "<span>#7</span> The theory of gravitation (10/17/61)",
        "m4a": "protectedaudio/mp4/FLP_7_01.mp4",
        "oga": "protectedaudio/ogg/FLP_7_01.ogg",
    },
    {
        "title": "<span>#8</span> Motion (10/20/61)",
        "m4a": "protectedaudio/mp4/FLP_8_01.mp4",
        "oga": "protectedaudio/ogg/FLP_8_01.ogg",
    },
    {
        "title": "<span>#9</span> Newton's laws of dynamics (10/24/61)",
        "m4a": "protectedaudio/mp4/FLP_9_01.mp4",
        "oga": "protectedaudio/ogg/FLP_9_01.ogg",
    },
    {
        "title": "<span>#10</span> Conservation of momentum (10/28/61)",
        "m4a": "protectedaudio/mp4/FLP_10_01.mp4",
        "oga": "protectedaudio/ogg/FLP_10_01.ogg",
    },
    {
        "title": "<span>#11</span> Vectors(11/3/61)",
        "m4a": "protectedaudio/mp4/FLP_11_01.mp4",
        "oga": "protectedaudio/ogg/FLP_11_01.ogg",
    },
    {
        "title": "<span>#12</span> On force(11/7/61)",
        "m4a": "protectedaudio/mp4/FLP_12_01.mp4",
        "oga": "protectedaudio/ogg/FLP_12_01.ogg",
    },
    {
        "title": "<span>#13</span> Work and potential energy (11/10/61)",
        "m4a": "protectedaudio/mp4/FLP_13_01.mp4",
        "oga": "protectedaudio/ogg/FLP_13_01.ogg",
    },
    {
        "title": "<span>#14</span> Work and potential energy, second try (11/14/61)",
        "m4a": "protectedaudio/mp4/FLP_14_01.mp4",
        "oga": "protectedaudio/ogg/FLP_14_01.ogg",
    },
    {
        "title": "<span>#15</span> Relativity (11/17/61)",
        "m4a": "protectedaudio/mp4/FLP_15_01.mp4",
        "oga": "protectedaudio/ogg/FLP_15_01.ogg",
    },
    {
        "title": "<span>#16</span> Relativistic energy and momentum (11/21/61)",
        "m4a": "protectedaudio/mp4/FLP_16_01.mp4",
        "oga": "protectedaudio/ogg/FLP_16_01.ogg",
    },
    {
        "title": "<span>#17</span> Space-time (11/28/61)",
        "m4a": "protectedaudio/mp4/FLP_17_01.mp4",
        "oga": "protectedaudio/ogg/FLP_17_01.ogg",
    },
    {
        "title": "<span class='nonum'></span> Review Lecture A (12/1/61)",
        "m4a": "protectedaudio/mp4/FLP_RevA_01.mp4",
        "oga": "protectedaudio/ogg/FLP_RevA_01.ogg",
    },
    {
        "title": "<span class='nonum'></span> Review Lecture B (12/5/61)",
        "m4a": "protectedaudio/mp4/FLP_RevB_01.mp4",
        "oga": "protectedaudio/ogg/FLP_RevB_01.ogg",
    },
    {
        "title": "<span class='nonum'></span> Review Lecture C (12/8/61)",
        "m4a": "protectedaudio/mp4/FLP_RevC_01.mp4",
        "oga": "protectedaudio/ogg/FLP_RevC_01.ogg",
    },
    {
        "title": "<span>#18</span> Rotation in two dimensions (1/5/62)",
        "m4a": "protectedaudio/mp4/FLP_18_01.mp4",
        "oga": "protectedaudio/ogg/FLP_18_01.ogg",
    },
    {
        "title": "<span>#19</span> Center of mass; moment of inertia (1/9/62)",
        "m4a": "protectedaudio/mp4/FLP_19_01.mp4",
        "oga": "protectedaudio/ogg/FLP_19_01.ogg",
    },
    {
        "title": "<span>#20</span> Rotation in space (1/12/62)",
        "m4a": "protectedaudio/mp4/FLP_20_01.mp4",
        "oga": "protectedaudio/ogg/FLP_20_01.ogg",
    },
    {
        "title": "<span>#21</span> Dynamical Effects and Their Applications (1/16/62)",
        "m4a": "protectedaudio/mp4/FLP_21_01.mp4",
        "oga": "protectedaudio/ogg/FLP_21_01.ogg",
    },
    {
        "title": "<span>#22</span> The harmonic oscillator (1/19/62)",
        "m4a": "protectedaudio/mp4/FLP_22_01.mp4",
        "oga": "protectedaudio/ogg/FLP_22_01.ogg",
    },
    {
        "title": "<span>#23</span> Algebra (1/23/62)",
        "m4a": "protectedaudio/mp4/FLP_23_01.mp4",
        "oga": "protectedaudio/ogg/FLP_23_01.ogg",
    },
    {
        "title": "<span>#24</span> Resonance(1/26/62)",
        "m4a": "protectedaudio/mp4/FLP_24_01.mp4",
        "oga": "protectedaudio/ogg/FLP_24_01.ogg",
    },
    {
        "title": "<span>#25</span> Transients(2/2/62)",
        "m4a": "protectedaudio/mp4/FLP_25_01.mp4",
        "oga": "protectedaudio/ogg/FLP_25_01.ogg",
    },
    {
        "title": "<span>#26</span> Linear systems (2/6/62)",
        "m4a": "protectedaudio/mp4/FLP_26_01.mp4",
        "oga": "protectedaudio/ogg/FLP_26_01.ogg",
    },
    {
        "title": "<span>#27</span> Optics: The principle of least time (2/9/62)",
        "m4a": "protectedaudio/mp4/FLP_27_01.mp4",
        "oga": "protectedaudio/ogg/FLP_27_01.ogg",
    },
    {
        "title": "<span>#28</span> Geometrical optics (2/13/62)",
        "m4a": "protectedaudio/mp4/FLP_28_01.mp4",
        "oga": "protectedaudio/ogg/FLP_28_01.ogg",
    },
    {
        "title": "<span>#29</span> Electromagnetic radiation (2/16/62)",
        "m4a": "protectedaudio/mp4/FLP_29_01.mp4",
        "oga": "protectedaudio/ogg/FLP_29_01.ogg",
    },
    {
        "title": "<span>#30</span> Interference (2/20/62)",
        "m4a": "protectedaudio/mp4/FLP_30_01.mp4",
        "oga": "protectedaudio/ogg/FLP_30_01.ogg",
    },
    {
        "title": "<span>#31</span> Diffraction (2/23/62)",
        "m4a": "protectedaudio/mp4/FLP_31_01.mp4",
        "oga": "protectedaudio/ogg/FLP_31_01.ogg",
    },
    {
        "title": "<span>#32</span> The origin of the refractive index (2/27/62)",
        "m4a": "protectedaudio/mp4/FLP_32_01.mp4",
        "oga": "protectedaudio/ogg/FLP_32_01.ogg",
    },
    {
        "title": "<span>#33</span> Radiation damping. Light scattering (3/2/62)",
        "m4a": "protectedaudio/mp4/FLP_33_01.mp4",
        "oga": "protectedaudio/ogg/FLP_33_01.ogg",
    },
    {
        "title": "<span>#34</span> Color vision (3/6/62)",
        "m4a": "protectedaudio/mp4/FLP_34_01.mp4",
        "oga": "protectedaudio/ogg/FLP_34_01.ogg",
    },
    {
        "title": "<span>#34A</span> Mechanisms of seeing (3/9/62)",
        "m4a": "protectedaudio/mp4/FLP_34A_01.mp4",
        "oga": "protectedaudio/ogg/FLP_34A_01.ogg",
    },
    {
        "title": "<span>#35</span> Polarization (3/27/62)",
        "m4a": "protectedaudio/mp4/FLP_35_01.mp4",
        "oga": "protectedaudio/ogg/FLP_35_01.ogg",
    },
    {
        "title": "<span>#36</span> Relativistic effects in radiation (3/30/62)",
        "m4a": "protectedaudio/mp4/FLP_36_01.mp4",
        "oga": "protectedaudio/ogg/FLP_36_01.ogg",
    },
    {
        "title": "<span>#37</span> Quantum behavior (4/3/62)",
        "m4a": "protectedaudio/mp4/FLP_37_01.mp4",
        "oga": "protectedaudio/ogg/FLP_37_01.ogg",
    },
    {
        "title": "<span>#38</span> The relation of wave and particle viewpoints (4/6/62)",
        "m4a": "protectedaudio/mp4/FLP_38_01.mp4",
        "oga": "protectedaudio/ogg/FLP_38_01.ogg",
    },
    {
        "title": "<span>#39</span> The relation of wave and particle viewpoints, second try (4/10/62)",
        "m4a": "protectedaudio/mp4/FLP_39_01.mp4",
        "oga": "protectedaudio/ogg/FLP_39_01.ogg",
    },
    {
        "title": "<span>#40</span> The kinetic theory of gases (4/13/62)",
        "m4a": "protectedaudio/mp4/FLP_40_01.mp4",
        "oga": "protectedaudio/ogg/FLP_40_01.ogg",
    },
    {
        "title": "<span>#41</span> The principles of statistical mechanics (4/17/62)",
        "m4a": "protectedaudio/mp4/FLP_41_01.mp4",
        "oga": "protectedaudio/ogg/FLP_41_01.ogg",
    },
    {
        "title": "<span>#41A</span> Brownian motion (4/20/62)",
        "m4a": "protectedaudio/mp4/FLP_41A_01.mp4",
        "oga": "protectedaudio/ogg/FLP_41A_01.ogg",
    },
    {
        "title": "<span>#42</span> Applications of kinetic theory (4/27/62)",
        "m4a": "protectedaudio/mp4/FLP_42_01.mp4",
        "oga": "protectedaudio/ogg/FLP_42_01.ogg",
    },
    {
        "title": "<span>#43</span> Diffusion (5/1/62)",
        "m4a": "protectedaudio/mp4/FLP_43_01.mp4",
        "oga": "protectedaudio/ogg/FLP_43_01.ogg",
    },
    {
        "title": "<span>#44</span> The laws of thermodynamics (5/4/62)",
        "m4a": "protectedaudio/mp4/FLP_44_01.mp4",
        "oga": "protectedaudio/ogg/FLP_44_01.ogg",
    },
    {
        "title": "<span>#45</span> Illustrations of thermodynamics (5/8/62)",
        "m4a": "protectedaudio/mp4/FLP_45_01.mp4",
        "oga": "protectedaudio/ogg/FLP_45_01.ogg",
    },
    {
        "title": "<span>#46</span> Ratchet and pawl (5/11/62)",
        "m4a": "protectedaudio/mp4/FLP_46_01.mp4",
        "oga": "protectedaudio/ogg/FLP_46_01.ogg",
    },
    {
        "title": "<span>#47</span> Sound. The wave equation (5/15/62)",
        "m4a": "protectedaudio/mp4/FLP_47_01.mp4",
        "oga": "protectedaudio/ogg/FLP_47_01.ogg",
    },
    {
        "title": "<span>#48</span> Beats (5/18/62)",
        "m4a": "protectedaudio/mp4/FLP_48_01.mp4",
        "oga": "protectedaudio/ogg/FLP_48_01.ogg",
    },
    {
        "title": "<span>#49</span> Modes (5/22/62)",
        "m4a": "protectedaudio/mp4/FLP_49_01.mp4",
        "oga": "protectedaudio/ogg/FLP_49_01.ogg",
    },
    {
        "title": "<span>#50</span> Harmonics (5/25/62)",
        "m4a": "protectedaudio/mp4/FLP_50_01.mp4",
        "oga": "protectedaudio/ogg/FLP_50_01.ogg",
    },
    {
        "title": "<span>#51</span> Waves (5/29/62)",
        "m4a": "protectedaudio/mp4/FLP_51_01.mp4",
        "oga": "protectedaudio/ogg/FLP_51_01.ogg",
    },
    {
        "title": "<span>#52</span> Symmetry in physical laws (6/1/62)",
        "m4a": "protectedaudio/mp4/FLP_52_01.mp4",
        "oga": "protectedaudio/ogg/FLP_52_01.ogg",
    },
    {
        "title": "<span>#S1</span> Electromagnetism (9/27/62)",
        "m4a": "protectedaudio/mp4/FLP_S1_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S1_01.ogg",
    },
    {
        "title": "<span>#S2</span> Differential calculus of vector fields (10/1/62)",
        "m4a": "protectedaudio/mp4/FLP_S2_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S2_01.ogg",
    },
    {
        "title": "<span>#S3</span> Integral vector calculus (10/4/62)",
        "m4a": "protectedaudio/mp4/FLP_S3_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S3_01.ogg",
    },
    {
        "title": "<span>#S4</span> Electrostatics (10/8/62)",
        "m4a": "protectedaudio/mp4/FLP_S4_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S4_01.ogg",
    },
    {
        "title": "<span>#S5</span> Application of Gauss' law (10/11/62)",
        "m4a": "protectedaudio/mp4/FLP_S5_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S5_01.ogg",
    },
    {
        "title": "<span>#S6</span> The electric field in various circumstances (10/15/62)",
        "m4a": "protectedaudio/mp4/FLP_S6_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S6_01.ogg",
    },
    {
        "title": "<span>#S7</span> The electric field in various circumstances II (10/18/62)",
        "m4a": "protectedaudio/mp4/FLP_S7_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S7_01.ogg",
    },
    {
        "title": "<span>#S8</span> Electrostatic energy (10/22/62)",
        "m4a": "protectedaudio/mp4/FLP_S8_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S8_01.ogg",
    },
    {
        "title": "<span>#S9</span> Electricity in the atmosphere (10/25/62)",
        "m4a": "protectedaudio/mp4/FLP_S9_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S9_01.ogg",
    },
    {
        "title": "<span>#S10</span> Dielectrics (11/1/62)",
        "m4a": "protectedaudio/mp4/FLP_S10_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S10_01.ogg",
    },
    {
        "title": "<span>#S11</span> Inside dielectrics (11/5/62)",
        "m4a": "protectedaudio/mp4/FLP_S11_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S11_01.ogg",
    },
    {
        "title": "<span>#S12</span> Electrostatic analogs (11/8/62)",
        "m4a": "protectedaudio/mp4/FLP_S12_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S12_01.ogg",
    },
    {
        "title": "<span>#S13</span> Magnetostatics (11/12/62)",
        "m4a": "protectedaudio/mp4/FLP_S13_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S13_01.ogg",
    },
    {
        "title": "<span>#S14</span> The magnetic field in various circumstances (11/15/62)",
        "m4a": "protectedaudio/mp4/FLP_S14_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S14_01.ogg",
    },
    {
        "title": "<span>#S15</span> The vector potential (11/19/62)",
        "m4a": "protectedaudio/mp4/FLP_S15_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S15_01.ogg",
    },
    {
        "title": "<span>#S16</span> Induction (11/26/62)",
        "m4a": "protectedaudio/mp4/FLP_S16_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S16_01.ogg",
    },
    {
        "title": "<span>#S17</span> Induction II (11/29/62)",
        "m4a": "protectedaudio/mp4/FLP_S17_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S17_01.ogg",
    },
    {
        "title": "<span>#S18</span> The Maxwell equations (12/3/62)",
        "m4a": "protectedaudio/mp4/FLP_S18_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S18_01.ogg",
    },
    {
        "title": "<span>#S19</span> The principle of least action (12/6/62)",
        "m4a": "protectedaudio/mp4/FLP_S19_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S19_01.ogg",
    },
    {
        "title": "<span>#S20</span> Solutions of Maxwell's equations (in free space) (1/3/63)",
        "m4a": "protectedaudio/mp4/FLP_S20_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S20_01.ogg",
    },
    {
        "title": "<span>#S21</span> Solutions of Maxwell's equations (with currents and charges) (1/7/63)",
        "m4a": "protectedaudio/mp4/FLP_S21_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S21_01.ogg",
    },
    {
        "title": "<span>#S22</span> A.C. circuits (1/10/63)",
        "m4a": "protectedaudio/mp4/FLP_S22_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S22_01.ogg",
    },
    {
        "title": "<span>#S23</span> Cavity resonators (1/14/63)",
        "m4a": "protectedaudio/mp4/FLP_S23_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S23_01.ogg",
    },
    {
        "title": "<span>#S24</span> Wave guides (1/17/63)",
        "m4a": "protectedaudio/mp4/FLP_S24_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S24_01.ogg",
    },
    {
        "title": "<span>#S25</span> Electrodynamics in relativistic notation (1/21/63)",
        "m4a": "protectedaudio/mp4/FLP_S25_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S25_01.ogg",
    },
    {
        "title": "<span>#S26</span> Lorentz transformation of the fields (1/24/63)",
        "m4a": "protectedaudio/mp4/FLP_S26_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S26_01.ogg",
    },
    {
        "title": "<span>#S27</span> Field energy and field momentum (1/31/63)",
        "m4a": "protectedaudio/mp4/FLP_S27_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S27_01.ogg",
    },
    {
        "title": "<span>#S28</span> Electromagnetic mass (2/4/63)",
        "m4a": "protectedaudio/mp4/FLP_S28_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S28_01.ogg",
    },
    {
        "title": "<span>#S29</span> The motion of charges in electric and magnetic fields (2/7/63)",
        "m4a": "protectedaudio/mp4/FLP_S29_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S29_01.ogg",
    },
    {
        "title": "<span>#S30</span> Crystals (2/10/63)",
        "m4a": "protectedaudio/mp4/FLP_S30_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S30_01.ogg",
    },
    {
        "title": "<span>#S31</span> Tensors (2/14/63)",
        "m4a": "protectedaudio/mp4/FLP_S31_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S31_01.ogg",
    },
    {
        "title": "<span>#S32</span> Refractive index of dense materials (2/18/63)",
        "m4a": "protectedaudio/mp4/FLP_S32_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S32_01.ogg",
    },
    {
        "title": "<span>#S33</span> Reflection from surfaces (2/21/63)",
        "m4a": "protectedaudio/mp4/FLP_S33_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S33_01.ogg",
    },
    {
        "title": "<span>#S34</span> Diamagnetism and Paramagnetism (2/25/63)",
        "m4a": "protectedaudio/mp4/FLP_S34_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S34_01.ogg",
    },
    {
        "title": "<span>#S35</span> Magnetic resonance (2/28/63)",
        "m4a": "protectedaudio/mp4/FLP_S35_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S35_01.ogg",
    },
    {
        "title": "<span>#S36</span> Ferromagnetism (3/4/63)",
        "m4a": "protectedaudio/mp4/FLP_S36_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S36_01.ogg",
    },
    {
        "title": "<span>#S37</span> Magnetic materials (3/7/63)",
        "m4a": "protectedaudio/mp4/FLP_S37_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S37_01.ogg",
    },
    {
        "title": "<span>#S38</span> Elasticity (3/28/63)",
        "m4a": "protectedaudio/mp4/FLP_S38_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S38_01.ogg",
    },
    {
        "title": "<span>#S39</span> Elastic materials (4/1/63)",
        "m4a": "protectedaudio/mp4/FLP_S39_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S39_01.ogg",
    },
    {
        "title": "<span>#S40</span> Flow of dry water (4/4/63)",
        "m4a": "protectedaudio/mp4/FLP_S40_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S40_01.ogg",
    },
    {
        "title": "<span>#S41</span> Flow of wet water (4/8/63)",
        "m4a": "protectedaudio/mp4/FLP_S41_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S41_01.ogg",
    },
    {
        "title": "<span>#S42</span> Probability amplitudes (4/11/63)",
        "m4a": "protectedaudio/mp4/FLP_S42_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S42_01.ogg",
    },
    {
        "title": "<span>#S43</span> Identical particles (4/15/63)",
        "m4a": "protectedaudio/mp4/FLP_S43_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S43_01.ogg",
    },
    {
        "title": "<span>#S44</span> Spin one (4/18/63)",
        "m4a": "protectedaudio/mp4/FLP_S44_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S44_01.ogg",
    },
    {
        "title": "<span>#S45</span> Spin one-half (4/22/63)",
        "m4a": "protectedaudio/mp4/FLP_S45_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S45_01.ogg",
    },
    {
        "title": "<span>#S46</span> The dependence of amplitudes on time (4/29/63)",
        "m4a": "protectedaudio/mp4/FLP_S46_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S46_01.ogg",
    },
    {
        "title": "<span>#S47</span> The Hamiltonian matrix (5/2/63)",
        "m4a": "protectedaudio/mp4/FLP_S47_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S47_01.ogg",
    },
    {
        "title": "<span>#S48</span> The ammonia maser (5/6/63)",
        "m4a": "protectedaudio/mp4/FLP_S48_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S48_01.ogg",
    },
    {
        "title": "<span>#S49</span> Other two-state systems (5/9/63)",
        "m4a": "protectedaudio/mp4/FLP_S49_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S49_01.ogg",
    },
    {
        "title": "<span>#S50</span> Two-state systems, cont. (5/13/63)",
        "m4a": "protectedaudio/mp4/FLP_S50_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S50_01.ogg",
    },
    {
        "title": "<span>#S51</span> Hyperfine splitting in hydrogen (5/16/63)",
        "m4a": "protectedaudio/mp4/FLP_S51_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S51_01.ogg",
    },
    {
        "title": "<span>#S52</span> Conservation of angular momentum (5/20/63)",
        "m4a": "protectedaudio/mp4/FLP_S52_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S52_01.ogg",
    },
    {
        "title": "<span>#S53</span> Angular momentum continued (5/23/63)",
        "m4a": "protectedaudio/mp4/FLP_S53_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S53_01.ogg",
    },
    {
        "title": "<span>#S53A</span> Special Lecture:Curved space (5/25/63)",
        "m4a": "protectedaudio/mp4/FLP_S53A_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S53A_01.ogg",
    },
    {
        "title": "<span>#S54</span> Dependence of space amplitudes (5/27/63)",
        "m4a": "protectedaudio/mp4/FLP_S54_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S54_01.ogg",
    },
    {
        "title": "<span>#S56</span> Propagation in a crystal lattice (5/7/64)",
        "m4a": "protectedaudio/mp4/FLP_S56_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S56_01.ogg",
    },
    {
        "title": "<span>#S57</span> Semiconductors (5/11/64)",
        "m4a": "protectedaudio/mp4/FLP_S57_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S57_01.ogg",
    },
    {
        "title": "<span>#S58</span> The independent particle approximation (5/14/64)",
        "m4a": "protectedaudio/mp4/FLP_S58_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S58_01.ogg",
    },
    {
        "title": "<span>#S59</span> The dependence of amplitudes on positions in space (5/18/64)",
        "m4a": "protectedaudio/mp4/FLP_S59_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S59_01.ogg",
    },
    {
        "title": "<span>#S60</span> Symmetry and conservation laws (5/21/64)",
        "m4a": "protectedaudio/mp4/FLP_S60_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S60_01.ogg",
    },
    {
        "title": "<span>#S61</span> Angular momentum (5/25/64)",
        "m4a": "protectedaudio/mp4/FLP_S61_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S61_01.ogg",
    },
    {
        "title": "<span>#S62</span> The hydrogen atom and the periodic table (5/28/64)",
        "m4a": "protectedaudio/mp4/FLP_S62_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S62_01.ogg",
    },
    {
        "title": "<span>#S63</span> Operators (6/1/64)",
        "m4a": "protectedaudio/mp4/FLP_S63_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S63_01.ogg",
    },
    {
        "title": "<span>#S64</span> The Schrödinger equation in a classical context: superconductivity (6/4/64)",
        "m4a": "protectedaudio/mp4/FLP_S64_01.mp4",
        "oga": "protectedaudio/ogg/FLP_S64_01.ogg",
    },
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download Feynman Lectures on Physics audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Download to default 'out' directory
  %(prog)s -o downloads              # Download to 'downloads' directory
  %(prog)s --no-date                 # Don't include lecture date in filenames
""",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default="out",
        help="Output directory for downloaded files (default: 'out')",
    )

    parser.add_argument(
        "--no-date",
        action="store_true",
        help="Don't include lecture date in filename",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["m4a", "ogg"],
        default="m4a",
        help="Audio format to download (default: m4a)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files (default: skip existing files)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    return parser.parse_args()


def signal_handler(signum, frame):
    print("\nDownload interrupted. Cleaning up...")
    sys.exit(1)


def clean_title(title):
    """Remove HTML tags and date from title."""
    return re.sub(DATE_REGEX, "", re.sub(TAG_REGEX, "", title)).strip()


def extract_date(title):
    """Extract and format date from title."""
    match = re.search(DATE_REGEX, title)
    if not match:
        raise ValueError(f"Invalid date format in title: {title}")

    month, day, year = match.groups()
    if len(year) == 2:
        year = "19" + year
    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"


def build_filename(title, no_date, format_ext):
    """Build filename from title and options."""
    clean = clean_title(title)
    if not no_date:
        date = extract_date(title)
        return f"{date} - {clean}.{format_ext}"
    return f"{clean}.{format_ext}"


def download_file(url, path, referer):
    """Download a file to a temporary location, then move to final path."""
    temp_fd, temp_path = tempfile.mkstemp(
        suffix=f".tmp.{os.path.splitext(path)[1][1:]}",
        dir=os.path.dirname(path),
        prefix="flp_download_",
    )

    try:
        response = requests.get(
            url,
            headers={"Referer": referer},
            stream=True,
        )
        response.raise_for_status()

        with os.fdopen(temp_fd, "wb") as temp_file:
            temp_file.write(response.content)

        os.rename(temp_path, path)
        temp_path = None

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def main():
    args = parse_args()
    signal.signal(signal.SIGINT, signal_handler)

    os.makedirs(args.output_dir, exist_ok=True)
    if args.verbose:
        print(f"Created directory: {args.output_dir}")

    for i, item in enumerate(FLP_PLAYLIST, 1):
        title = item["title"]
        clean = clean_title(title)

        audio_key = "m4a" if args.format == "m4a" else "oga"
        file_ext = args.format if args.format == "m4a" else "ogg"

        filename = build_filename(title, args.no_date, file_ext)
        path = os.path.join(args.output_dir, filename)

        if os.path.exists(path) and not args.overwrite:
            if args.verbose:
                print(f"Skipping {clean} (already exists).")
            continue

        print(
            f"\x1b[2K[{i}/{len(FLP_PLAYLIST)}] Downloading \x1b[3m{clean}\x1b[0m...",
            end="\r",
        )

        try:
            url = urllib.parse.urljoin(BASE_URL, item[audio_key])
            download_file(url, path, REFERER)
            print(
                f"\x1b[2K[{i}/{len(FLP_PLAYLIST)}] Downloaded \x1b[3m{clean}\x1b[0m.",
                end="\r",
            )

        except requests.RequestException as e:
            print(f"\x1b[2K[{i}/{len(FLP_PLAYLIST)}] Failed to download {clean}: {e}")
            if args.verbose:
                traceback.print_exc()

        except KeyboardInterrupt:
            print(f"\nDownload of {clean} interrupted.")
            raise


if __name__ == "__main__":
    main()
